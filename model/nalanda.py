from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
from model.session import Session

# Needed to download files
import os
import re
from model.utilities import extract_first_form


class NalandaSession:
    NALANDA_LOGIN_URL = 'http://nalanda.bits-pilani.ac.in/login/index.php'
    NALANDA_HOME_URL = 'http://nalanda.bits-pilani.ac.in/my/index.php'
    NALANDA_SEARCH_URL = 'http://nalanda.bits-pilani.ac.in/course/search.php'
    NALANDA_RESOURCE_URL = 'http://nalanda.bits-pilani.ac.in/course/resources.php'
    NALANDA_COURSE_URL = 'http://nalanda.bits-pilani.ac.in/course/view.php'

    def __init__(self, session):
        assert isinstance(session, Session)
        self.session = session

    def get_oauth(self):
        self.session.cookies.clear()
        nalanda_login_page = self.session.get(self.NALANDA_LOGIN_URL).text
        soup = BeautifulSoup(nalanda_login_page, 'html.parser')
        oauth_url = soup.find('a', class_="btn").get('href')
        return oauth_url

    def nalanda_login(self, username, password):
        assert isinstance(username, str)
        assert isinstance(password, str)
        # nalanda_login_page = self.session.get(url=self.NALANDA_LOGIN_URL).text
        # action, _ = extract_first_form(nalanda_login_page)
        params = {'username': username, 'password': password}
        response_html = self.session.post(url=self.NALANDA_LOGIN_URL, data=params, allow_redirects=True).text
        action, params = extract_first_form(response_html)
        if action == self.NALANDA_LOGIN_URL:
            # login failed
            return False
        return True

    def registered_courses(self):
        nalanda_main_page = self.session.get(self.NALANDA_HOME_URL).text
        soup = BeautifulSoup(nalanda_main_page, 'html.parser')
        courses_links = soup.select('.media-heading > a')
        courses = set(course_link.text for course_link in courses_links)
        return courses

    def search_courses(self, search_string):
        assert isinstance(search_string, str)
        query_params = {"search": search_string, "perpage": "all"}
        search_results = self.session.get(self.NALANDA_SEARCH_URL, params=query_params).text
        soup = BeautifulSoup(search_results, 'html.parser')
        course_boxs = soup.select('.coursebox')
        courses = list()
        for course_box in course_boxs:
            url = course_box.find("a").get("href")  # Course URL
            course_id = parse_qs(urlparse(url).query)['id'][0]  # COURSE ID
            title = course_box.find("a").text.replace("/", ",").strip()  # Course title
            if course_box.find("ul", class_='teachers'):  # If teacher is present
                teacher = course_box.find("ul", class_='teachers').find('a').text  # update where ever present
                courses.append(Course(course_id=course_id, title=title, teacher=teacher))
            else:
                courses.append(Course(course_id=course_id, title=title))
        return courses

    # def get_attachments(session, course_id, from_announcements):
    def get_all_attachments(self, course_id, from_announcements=False):
        assert isinstance(course_id, str)
        assert isinstance(from_announcements, bool)
        query_parameters = {"id": course_id}
        resource_page = self.session.get(self.NALANDA_RESOURCE_URL, params=query_parameters).text
        soup = BeautifulSoup(resource_page, 'html.parser')
        attachment_urls = {}
        for html_link in soup.find_all('a'):
            link = html_link.get('href')
            folder_name = html_link.text.strip()  # Construct the folder name to download to
            if '/mod/resource/view.php' in link:  # Check if url is pointing to document
                if folder_name not in attachment_urls:
                    attachment_urls[folder_name] = set()
                # Add the resource link on the resource page
                attachment_urls[folder_name].add(link)
            elif '/mod/folder/view.php' in link:  # Check if url pointing to folder
                if folder_name not in attachment_urls:
                    attachment_urls[folder_name] = set()
                # Copy all links from that folder
                attachment_urls[folder_name].update(self.__get_attachments_from_folder(link))
        if from_announcements:  # If ANNOUNCEMENT SECTION(S) ARE ALSO CONSIDERED
            # Note: There are multiple announcement sections
            # Each with its own set of announcements/discussions
            # Thus we need to get attachment links from each discussion forum in each of the announcement sections
            # Assuming Different announcement titles in different announcement sections ASSUMPTION
            # Load the course page and get the Different Announcement Sections links(URLs)
            parameters = {"id": course_id}
            forum_links = self.__filter_links_on_page__(self.NALANDA_COURSE_URL, '/mod/forum/view.php', parameters)
            for forum_link in forum_links:
                attachment_urls.update(self.__get_attachments_from_forum(forum_link))
        # return attachment_urls
        filenames_to_attachment_urls = {}
        for folder_name in attachment_urls:
            for attachment_url in attachment_urls[folder_name]:
                filename = self.get_download_attachment_filename(attachment_url)
                if filename:
                    path_to_file = '{}/{}'.format(folder_name, filename)
                    filenames_to_attachment_urls[path_to_file] = attachment_url
        return filenames_to_attachment_urls

    def __filter_links_on_page__(self, page_link, filter_string, params=None):
        # This function obtains all links in the given page_link using a GET request with given parameters
        # and gathers all links and filters the links based on given filter_string
        assert isinstance(page_link, str)
        assert isinstance(filter_string, str)
        if params:
            page = self.session.get(page_link, params=params).text
        else:
            page = self.session.get(page_link).text
        soup = BeautifulSoup(page, 'html.parser')
        links = map(lambda html_link: html_link.get('href'), soup.find_all('a', {'href': True}))
        filtered_links = filter(lambda link: filter_string in link, links)
        return set(filtered_links)

    def __get_attachments_from_folder(self, folder_link):
        attachment_links = self.__filter_links_on_page__(folder_link, '/mod_folder/content/')
        return attachment_links

    def __get_attachments_from_forum(self, forum_link):
        forum_page = self.session.get(forum_link).text
        soup = BeautifulSoup(forum_page, 'html.parser')
        discussion_links_to_titles = \
            dict(map(lambda html_link: (html_link.get('href'), html_link.text), soup.select('.starter > a')))
        discussion_links = filter(lambda link: '/mod/forum/discuss.php' in link, discussion_links_to_titles.keys())
        attachment_urls = {}
        for discussion_link in discussion_links:
            attachment_links = self.__filter_links_on_page__(discussion_link, '/mod_forum/attachment/')
            if attachment_links:
                attachment_urls[discussion_links_to_titles[discussion_link]] = attachment_links
        return attachment_urls

    def get_download_attachment_filename(self, attachment_url):
        r = self.session.head(attachment_url, allow_redirects=True)
        if 'Content-Disposition' in r.headers:
            filename = re.findall("filename=(.+)", r.headers['Content-Disposition'])[0].replace('"', '')
            return filename
        return None

    def download_attachment(self, attachment_url, filepath=None):
        """Saves the attachment pointed by url to a file in the specified directory"""
        r = self.session.get(attachment_url)
        if 'Content-Disposition' in r.headers:
            # Get the filename from Content=Disposition Header
            filename = re.findall("filename=(.+)", r.headers['Content-Disposition'])[0].replace('"', '')
            # Write bytes of content to file
            if filepath:
                os.makedirs(filepath, exist_ok=True)
                with open(os.path.join(filepath, filename), 'wb') as f:
                    f.write(r.content)
            else:
                with open(filename, 'wb') as f:
                    f.write(r.content)
            return filename
        return None


class Course:
    def __init__(self, course_id, title, teacher=None):
        self.course_id = course_id
        self.title = title
        self.teacher = teacher

    def __str__(self):
        if self.teacher:
            return "{}. {} ({})".format(self.course_id, self.title, self.teacher)
        return "{}. {}".format(self.course_id, self.title)
