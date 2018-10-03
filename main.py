# import logging
from controller.logincontroller import LoginController
from controller.downloadcontroller import NalandaDownloaderController
from model.googleoauth import GoogleSession
from model.session import Session
from model.nalanda import NalandaSession
from view.authenticationwindow import AuthenticationWindow
from view.nalandadownloader import NalandaDownloader

# logging.basicConfig(format='%(asctime)s:%(name)s:LINE %(lineno)d:%(levelname)s:%(message)s', level=logging.DEBUG)

if __name__ == '__main__':
    session = Session()
    nalanda_session = NalandaSession(session=session)
    google_session = GoogleSession(session=session, nalanda_session=nalanda_session)
    login_window = AuthenticationWindow()
    login_controller = LoginController(login_window=login_window, google_session=google_session)
    nalanda_downloader = NalandaDownloader()
    nalanda_controller = NalandaDownloaderController(nalanda_downloader=nalanda_downloader,
                                                     nalanda_session=nalanda_session)