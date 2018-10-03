from model.session import Session
from bs4 import BeautifulSoup
from model.nalanda import NalandaSession
import enum

CAPTCHA_FILE_NAME = 'captcha.jpg'


def extract_first_form(html_page):
    soup = BeautifulSoup(html_page, 'html.parser')
    form_element = soup.find('form', {'action': True})
    action_url = form_element.get('action')
    input_fields = form_element.find_all('input', {'name': True})
    parameters = {input_field.get('name'): input_field.get('value') for input_field in input_fields}
    print("ACTION URL:", action_url)
    print("PARAMETERS:", parameters)
    return action_url, parameters


class InternalState(enum.Enum):
    NOTHING = enum.auto()
    USERNAME = enum.auto()
    CAPTCHA = enum.auto()


class ReturnState(enum.Enum):
    OK = enum.auto()
    INVALID_USERNAME = enum.auto()
    INVALID_PASSWORD = enum.auto()
    REQUIRE_CAPTCHA = enum.auto()
    INVALID_ACCOUNT = enum.auto()


class GoogleSession:
    def __init__(self, session, nalanda_session):
        assert isinstance(session, Session)
        self.session = session
        assert isinstance(nalanda_session, NalandaSession)
        self.nalanda_session = nalanda_session
        self.state = InternalState.NOTHING
        self.password_parameters = None
        self.authenticate_page_url = None
        self.prevusername = None
        self.prevpassword = None

    def authorize(self, username, password, captcha=''):
        assert isinstance(username, str)
        assert isinstance(password, str)
        assert isinstance(captcha, str)
        # Set the state here (STATE MANAGEMENT LOGIC HERE)
        if not self.prevusername or not self.prevpassword:
            self.state = InternalState.NOTHING
        elif self.prevusername != username:
            self.state = InternalState.NOTHING
        # Assuming Username and Password are not empty
        if self.state == InternalState.NOTHING:
            oauth_url = self.nalanda_session.get_oauth()
            google_login_page = self.session.get(oauth_url).text
            password_page_url, username_parameters = extract_first_form(google_login_page)
            username_parameters['Email'] = username
            gmail_password_page = self.session.post(password_page_url, data=username_parameters).text
            authenticate_page_url, password_parameters = extract_first_form(gmail_password_page)
            if authenticate_page_url == 'https://accounts.google.com/signin/v1/lookup':
                return ReturnState.INVALID_USERNAME
            self.password_parameters = password_parameters
            self.authenticate_page_url = authenticate_page_url
            self.state = InternalState.USERNAME

        if self.state == InternalState.USERNAME or self.state == InternalState.CAPTCHA:
            if self.state == InternalState.USERNAME:
                self.password_parameters['Passwd'] = password
            if self.state == InternalState.CAPTCHA:
                self.password_parameters['Passwd'] = password
                self.password_parameters['logincaptcha'] = captcha

            password_ok_page = self.session.post(self.authenticate_page_url, data=self.password_parameters).text
            page_url, page_input_params = extract_first_form(password_ok_page)
            if page_url == 'https://accounts.google.com/signin/challenge/sl/password':
                if 'logincaptcha' in page_input_params:
                    self.password_parameters = page_input_params
                    self.authenticate_page_url = page_url
                    self.state = InternalState.CAPTCHA
                    self.save_captcha_image(page_input_params)
                    return ReturnState.REQUIRE_CAPTCHA
                else:
                    self.state = InternalState.USERNAME
                    return ReturnState.INVALID_PASSWORD
            elif page_url == 'https://accounts.google.com/signin/v1/lookup':
                self.state = InternalState.NOTHING
                return ReturnState.INVALID_USERNAME
            elif page_url == 'http://nalanda.bits-pilani.ac.in/login/index.php':
                self.state = InternalState.NOTHING
                return ReturnState.INVALID_ACCOUNT
            else:
                return ReturnState.OK

    def save_captcha_image(self, captcha_url):
        image_contents = self.session.get(captcha_url).content
        with open(CAPTCHA_FILE_NAME, 'wb') as image:
            image.write(image_contents)
