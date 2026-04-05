# setup_search.py
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import *
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

SEARCH_ENDPOINT = "https://YOUR_SEARCH.search.windows.net"
SEARCH_KEY = "YOUR_SEARCH_ADMIN_KEY"
INDEX_NAME = "college-knowledge"

# Create Index
index_client = SearchIndexClient(SEARCH_ENDPOINT, AzureKeyCredential(SEARCH_KEY))

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SearchableField(name="title", type=SearchFieldDataType.String),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SimpleField(name="category", type=SearchFieldDataType.String, filterable=True),
]

index = SearchIndex(name=INDEX_NAME, fields=fields)
index_client.create_or_update_index(index)

# Upload College Data
search_client = SearchClient(SEARCH_ENDPOINT, INDEX_NAME, AzureKeyCredential(SEARCH_KEY))

college_data = [
    {"id": "1", "title": "Admission Process", "category": "admissions",
     "content": "Admissions open in June. Apply via the college portal. Required docs: 10th & 12th marksheets, ID proof, passport photo."},
    {"id": "2", "title": "Fee Structure", "category": "fees",
     "content": "B.Tech: ₹85,000/year. MBA: ₹1,20,000/year. Hostel: ₹45,000/year. Scholarships available for merit students."},
    {"id": "3", "title": "Courses Offered", "category": "academics",
     "content": "We offer B.Tech (CS, ECE, Mech, Civil), MBA, MCA, BCA, B.Sc. Lateral entry available for diploma holders."},
    {"id": "4", "title": "Campus Facilities", "category": "campus",
     "content": "Library open 7AM-10PM. Wi-Fi across campus. Sports complex, gym, cafeteria, ATM, and medical center available."},
    {"id": "5", "title": "Exam Schedule", "category": "exams",
     "content": "Semester exams in November and May. Internal exams every 6 weeks. Results published within 30 days on the student portal."},
    {"id": "6", "title": "Placement Cell", "category": "placements",
     "content": "Placement drives from September to March. Average package: ₹6.5 LPA. Top recruiters: TCS, Infosys, Wipro, Cognizant, Amazon."},
    {"id": "7", "title": "Contact Info", "category": "contact",
     "content": "Main office: +91-XXXXXXXXXX. Email: info@college.edu. Office hours: Mon-Sat 9AM-5PM."},
]

search_client.upload_documents(documents=college_data)
print("✅ College knowledge base uploaded!")