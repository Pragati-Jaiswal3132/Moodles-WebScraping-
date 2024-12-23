
import requests
from bs4 import BeautifulSoup

# Define login credentials
username = 'pragatijaiswal3132@gmail.com'
password = 'Pragati3132@'
baseurl = 'https://edqueries.com/'

# Function to log in to the website
def login(user, pwd):
    session = requests.Session()
    login_url = baseurl + '/my-account-2/'
    login_data = {
        'log': user,
        'pwd': pwd,
        'wp-submit': 'Log In',
        'redirect_to': 'https://edqueries.com/eb-courses/',
        'testcookie': '1'
    }
    response = session.post(login_url, data=login_data)
    if response.status_code == 200:
        print("Login successful")
    else:
        print(f"Login failed with status code {response.status_code}")
        exit()
    return session

# Function to parse course titles from the 'My Courses' page
def get_courses(session):
    courses_url = baseurl + 'eb-courses/'
    response = session.get(courses_url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        # Searching for course titles with the class 'eb-course-title'
        courses = soup.find_all('div', class_='eb-course-title')  # Corrected class name here
        if not courses:
            print("No courses found!")
            exit()
        else:
            print("Course Titles:")
            for idx, course in enumerate(courses, 1):
                title = course.get_text(strip=True)
                print(f"{idx}. {title}")
    else:
        print(f"Failed to fetch courses, status code {response.status_code}")
        exit()

def get_course_info(tag):
    course_info = {}
    
    # Extract URL from the <a> tag
    course_info['url'] = tag['href'] if tag.has_attr('href') else None
    # Extract course name and details from the caption
    caption_div = tag.find('div', class_='eb-course-title')
    if caption_div:
        course_info['course_name'] = caption_div.get_text(strip=True)
    
    return course_info

def fetch_course_activities(ses, course_name):
    # Fetch courses and locate the desired course
    courses_page = ses.get(baseurl + 'eb-courses/')
    if courses_page.status_code != 200:
        print(f"ERROR: Unable to fetch courses. {courses_page.status_code} {courses_page.reason}")
        return

    soup = BeautifulSoup(courses_page.text, 'html.parser')
    course_tags = soup.find_all('a', class_='wdm-course-thumbnail')

    selected_tag = None
    for tag in course_tags:
        course_info = get_course_info(tag)
        if course_info['course_name'] and course_info['course_name'].lower() == course_name.lower():
            selected_tag = tag
            break

    if not selected_tag:
        print(f"ERROR: Course '{course_name}' not found.")
        return

    # Extract course URL using get_course_info
    course_info = get_course_info(selected_tag)
    course_url = course_info.get('url')
    if not course_url:
        print(f"ERROR: No URL found for course '{course_name}'.")
        return

    print(f"Fetching activities for course: {course_info['course_name']}")
    print(f"Course URL: {course_url}")

    # Fetch course page to retrieve activities
    course_page = ses.get(course_url)
    if course_page.status_code != 200:
        print(f"ERROR: Unable to fetch course page. {course_page.status_code} {course_page.reason}")
        return

    # Check for 'Join' button with id='wdm-btn'
    course_soup = BeautifulSoup(course_page.text, 'html.parser')
    join_button = course_soup.find('a', id='wdm-btn')

    if join_button and join_button.has_attr('href'):
        join_url = join_button['href']
        print(f"'Join' button found! Redirecting to: {join_url}")

        # Fetch the join page
        join_page = ses.get(join_url)
        if join_page.status_code != 200:
            print(f"ERROR: Unable to fetch the join page. {join_page.status_code} {join_page.reason}")
            return

        # Parse activities from the join page
        join_soup = BeautifulSoup(join_page.text, 'html.parser')
        activity_divs = join_soup.find_all('div', class_='instancename')

        if not activity_divs:
            print("No activities found on the join page.")
            return

        print(f"Activities for course '{course_name}':")
        for i, div in enumerate(activity_divs, 1):
            activity_name = div.get_text(strip=True)
            print(f" {i}. {activity_name}")
    else:
        print(f"No 'Join' button found for the course '{course_name}'. Checking activities on the course page...")
        
        # Parse activities directly from the course page
        activity_spans = course_soup.find_all('span', class_='instancename')

        if not activity_spans:
            print("No activities found for this course.")
            return

        print(f"Activities for course '{course_name}':")
        for i, span in enumerate(activity_spans, 1):
            activity_name = span.get_text(strip=True)
            print(f" {i}. {activity_name}")


# Main process
print("Logging in...")
session = login(username, password)

print("Fetching courses...")
get_courses(session)
# Prompt user to input course name
course_name = input("Enter the course name to fetch activities: ").strip()

# Fetch and display activities for the specified course
fetch_course_activities(session, course_name)