from view.authenticationwindow import AuthenticationWindow
from model.googleoauth import GoogleSession, ReturnState, CAPTCHA_FILE_NAME
import threading


class LoginController:
    def __init__(self, login_window, google_session):
        assert isinstance(login_window, AuthenticationWindow)
        assert isinstance(google_session, GoogleSession)
        self.google_session = google_session
        self.login_window = login_window
        self.lock = threading.RLock()
        self.threads = list()
        self.login_window.set_submit_button_command(action=self.dispatcher(self.__handle_login))
        self.login_window.set_captcha_button_command(action=self.dispatcher(self.__handle_login))
        self.login_window.start_mainloop()
        for thread in self.threads:
            thread.join()
        self.login_window.__destroy__()

    def __create_and_insert_thread(self, method_to_call):
        thread = threading.Thread(target=self.__dispatch_method__, args=(method_to_call, ))
        self.threads.append(thread)
        return thread

    def dispatcher(self, method_to_call):
        return lambda: self.__create_and_insert_thread(method_to_call).start()

    def __dispatch_method__(self, method_to_call):
        if self.lock.acquire(blocking=False):
            self.login_window.update_busy_status('BUSY')
            try:
                method_to_call()
            finally:
                self.login_window.update_busy_status('')
                self.lock.release()
        else:
            self.login_window.update_status('Please Wait till Action is Completed.')

    def __handle_login(self):
        username = self.login_window.get_username()
        password = self.login_window.get_password()
        if not username:
            self.login_window.update_status('Enter Username.')
            return
        if not password:
            self.login_window.update_status('Enter Password.')
            return
        if self.login_window.is_captcha_enabled():
            captcha = self.login_window.get_captcha()
            return_status = self.google_session.authorize(username=username, password=password, captcha=captcha)
        else:
            return_status = self.google_session.authorize(username=username, password=password)
        if return_status == ReturnState.OK:
            self.login_window.__close__()
        elif return_status == ReturnState.INVALID_USERNAME:
            self.login_window.update_status('Invalid Username')
        elif return_status == ReturnState.INVALID_PASSWORD:
            self.login_window.update_status('Invalid Password')
        elif return_status == ReturnState.REQUIRE_CAPTCHA:
            self.login_window.view_captcha(CAPTCHA_FILE_NAME)
            self.login_window.update_status('Submit with Captcha')
        elif return_status == ReturnState.INVALID_ACCOUNT:
            self.login_window.update_status('Nalanda Doesn\'t Recognize Account.')
