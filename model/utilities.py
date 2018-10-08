from bs4 import BeautifulSoup


def extract_first_form(html_page):
    soup = BeautifulSoup(html_page, 'html.parser')
    form_element = soup.find('form', {'action': True})
    action_url = form_element.get('action')
    input_fields = form_element.find_all('input', {'name': True})
    parameters = {input_field.get('name'): input_field.get('value') for input_field in input_fields}
    print("ACTION URL:", action_url)
    print("PARAMETERS:", parameters)
    return action_url, parameters
