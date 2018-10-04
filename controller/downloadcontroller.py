import threading
from view.nalandadownloader import NalandaDownloader
from model.nalanda import NalandaSession
from os.path import dirname
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_COURSES_WORKERS = 5
MAX_DOWNLOAD_WORKERS = 5


class NalandaDownloaderController:
    def __init__(self, nalanda_downloader, nalanda_session):
        assert isinstance(nalanda_downloader, NalandaDownloader)
        assert isinstance(nalanda_session, NalandaSession)
        self.nalanda_downloader = nalanda_downloader
        self.nalanda_session = nalanda_session
        self.lock = threading.RLock()
        self.nalanda_downloader.set_search_button_command(self.dispatcher(self.__handle_course_search))
        self.nalanda_downloader.set_courses_button_command(self.dispatcher(self.__handle_courses_attachments))
        self.nalanda_downloader.set_downloads_button_command(self.dispatcher(self.__handle_download_attachments))
        self.nalanda_downloader.start_mainloop()
        self.courses = None
        self.downloads = None   # A Dictionary
        self.downloads_files = None   # The Dictionary Keys

    def dispatcher(self, method_to_call):
        return lambda: threading.Thread(target=self.__dispatch_method__, args=(method_to_call, )).start()

    def __dispatch_method__(self, method_to_call):
        if self.lock.acquire(blocking=False):
            self.nalanda_downloader.update_busy_status('BUSY')
            try:
                method_to_call()
            finally:
                self.nalanda_downloader.update_busy_status('')
                self.lock.release()
        else:
            self.nalanda_downloader.update_status('Please Wait till Action is Completed.')

    def __handle_course_search(self):
        search_string = self.nalanda_downloader.get_search_string()
        courses = self.nalanda_session.search_courses(search_string)
        if not courses:
            self.nalanda_downloader.update_status("No courses found with words '{}'".format(search_string))
        else:
            self.courses = courses
            self.nalanda_downloader.update_courses(courses)
            self.nalanda_downloader.update_status("'{}' courses found matching '{}'".format(len(courses), search_string))

    def __handle_courses_attachments(self):
        indices = self.nalanda_downloader.courses_selected()
        if not indices:
            self.nalanda_downloader.update_status("No courses selected.")
        else:
            from_announcements = self.nalanda_downloader.is_announcements_selected()
            selected_courses = map(lambda index: self.courses[index], indices)
            downloads = {}
            with ThreadPoolExecutor(max_workers=MAX_COURSES_WORKERS) as executor:
                future_to_course = {
                    executor.submit(self.nalanda_session.get_all_attachments, course.course_id, from_announcements): course
                    for course in selected_courses}
                for future in as_completed(future_to_course):
                    course = future_to_course[future]
                    self.nalanda_downloader.update_status("Fetched Attachments from {}".format(course.title))
                    filenames_to_attachment_urls = future.result()
                    for file_path in filenames_to_attachment_urls:
                        downloads['{}/{}'.format(course.title, file_path)] = filenames_to_attachment_urls[file_path]
            for course in selected_courses:
                self.nalanda_downloader.update_status("Fetching Attachments from {}".format(course.title))
                filenames_to_attachment_urls = \
                    self.nalanda_session.get_all_attachments(course.course_id, from_announcements)
                for file_path in filenames_to_attachment_urls:
                    downloads['{}/{}'.format(course.title, file_path)] = filenames_to_attachment_urls[file_path]
            if not downloads:
                self.nalanda_downloader.update_status("Nothing to download.")
            else:
                self.downloads = downloads
                self.downloads_files = list(downloads.keys())
                self.nalanda_downloader.update_downloads(self.downloads_files)
                self.nalanda_downloader.update_status("{} files to download.".format(len(self.downloads_files)))

    def __handle_download_attachments(self):
        indices = self.nalanda_downloader.downloads_selected()
        if not indices:
            self.nalanda_downloader.update_status("No downloads selected.")
        else:
            selected_files = list(map(lambda index: self.downloads_files[index], indices))
            file_count = len(selected_files)

            with ThreadPoolExecutor(max_workers=MAX_DOWNLOAD_WORKERS) as executor:
                for file_to_download in selected_files:
                    attachment_url = self.downloads[file_to_download]
                    folder_name = dirname(file_to_download)
                    executor.submit(self.__notify_on_download_completion, attachment_url, folder_name)
            self.nalanda_downloader.update_status('Downloaded {} files'.format(file_count))

    def __notify_on_download_completion(self, attachment_url, folder_name):
        filename = self.nalanda_session.download_attachment(attachment_url=attachment_url, filepath=folder_name)
        self.nalanda_downloader.update_status('Downloaded {} to\n{}'.format(filename, folder_name))
