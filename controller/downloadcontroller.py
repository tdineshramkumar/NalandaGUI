import threading
from view.nalandadownloader import NalandaDownloader
from model.nalanda import NalandaSession


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
        self.downloads_folders = None   # The Dictionary Keys

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
            for course in selected_courses:
                self.nalanda_downloader.update_status("Fetching Attachments from {}".format(course.title))
                attachment_urls = self.nalanda_session.get_all_attachments(course.course_id, from_announcements)
                for folder_name in attachment_urls:
                    if attachment_urls[folder_name]:
                        downloads['{}/{}'.format(course.title, folder_name)] = attachment_urls[folder_name]
            if not downloads:
                self.nalanda_downloader.update_status("Nothing to download.")
            else:
                self.downloads = downloads
                self.downloads_folders = list(downloads.keys())
                self.nalanda_downloader.update_downloads(self.downloads_folders)
                self.nalanda_downloader.update_status("{} topics to download.".format(len(self.downloads_folders)))

    def __handle_download_attachments(self):
        indices = self.nalanda_downloader.downloads_selected()
        if not indices:
            self.nalanda_downloader.update_status("No downloads selected.")
        else:
            selected_downloads = list(map(lambda index: self.downloads_folders[index], indices))
            file_count = 0
            folder_count = len(selected_downloads)
            for index, folder_name in enumerate(selected_downloads, 1):
                for attachment_url in self.downloads[folder_name]:
                    filename = \
                        self.nalanda_session.download_attachment(attachment_url=attachment_url, filepath=folder_name)
                    if filename:
                        self.nalanda_downloader.update_status('Downloaded {} to\n{}'.format(filename, folder_name))
                        file_count += 1
                self.nalanda_downloader.update_status('Downloaded {}/{} folders'.format(index, folder_count))
            self.nalanda_downloader.update_status('Downloaded {} files into {} folders.'.format(file_count, folder_count))