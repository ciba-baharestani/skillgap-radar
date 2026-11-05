from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

urls = [
   #"https://www.continuingstudies.udel.edu/instructional-design",
    #"https://www.swu.edu/academics/school-of-education/instructional-design-certificate/",
    #"https://drexel.edu/soe/academics/certificates/instructional-design-for-e-learning",
    #"https://www.wku.edu/online/grad-certs/instructional-design/index.php",
    #"https://ecampus.oregonstate.edu/online-degrees/graduate/instructional-design/curriculum.htm",
   "https://scs.georgetown.edu/programs/512/certificate-in-instructional-design",
    #"https://und.edu/programs/learning-analytics-cert/",
    #"https://www.roosevelt.edu/academics/programs/training-development-certificate",
    #"https://education.stthomas.edu/continuing-education/certificates/learning-technology-leadership-innovation",
    "https://ced.ncsu.edu/news-new/graduate/programs/certificate/learning-analytics",
    "https://peabody.vanderbilt.edu/academics/graduate-professional-certificates/learning-analytics/",
    "https://www.winona.edu/academics/colleges/education/education-studies-department/programs/training-development-graduate-certificate/",
    "https://uwgb.edu/certificate-programs/training-development",
    "https://www.ycp.edu/node/17299",
    "https://campus.kennesaw.edu/colleges-departments/bagwell/degrees-programs/specialist/eds-itec-advanced-track-technology-leadership/index.php",
]

for url in urls:
    parts = urlparse(url)
    robots_url = f"{parts.scheme}://{parts.netloc}/robots.txt"
    rp = RobotFileParser()
    rp.set_url(robots_url)
    try:
        rp.read()
        status = "ALLOWED" if rp.can_fetch("*", url) else "BLOCKED"
    except Exception as e:
        status = f"ERROR ({e})"
    print(status, "-", url)