from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from apiclient import errors
import base64
import email
import mailparser
from string import punctuation
import string
import re
from nltk.tokenize import RegexpTokenizer
from nltk.stem import WordNetLemmatizer
from nltk.stem.snowball import SnowballStemmer


# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

'''
def preprocess(text):
    words_list = ""
    sstemmer = SnowballStemmer("english")
    lemmatizer = WordNetLemmatizer()
    text = text.split()
    for w in text:
        w = lemmatizer.lemmatize(w)
        words_list = words_list + sstemmer.stem(w) + " "
    return words_list
'''
def preprocess(text):
	set(stopwords.words('english'))

	stop_words = set(stopwords.words('english'))

	word_tokens = word_tokenize(text)

	words_list = []
	for w in word_tokens:
        if w not in stop_words:
            words_list.append(w)

	Stem_words = []
	ps =PorterStemmer()
	for w in words_list:
        rootWord=ps.stem(w)
        Stem_words.append(rootWord)
	print(words_list)
	print(Stem_words)

def clean_text(text):
    # remove urls
    text = re.sub(r'http\S+', ' ', text)
    # or replace urls with word httpaddress
    # text = re.sub('(http|https)://[^\s]*', 'httpaddress', text)

    # replace email address with word emailaddress
    text = re.sub('[^\s]+@[^\s]+', ' ', text)

    # replace "$" with word "dollar".
    #text = re.sub('[$]+', ' ', text)

    # remove numbers
    #text = re.sub("\d+", ' ', text)
    # or replace numbers with word number
    #text = re.sub('[0-9]+', 'number', text)

    # remove html tags
    text = re.sub('<[^<>]+>', ' ', text)
    # remove new lines
    text = text.replace('\\n', ' ')
    text = text.replace('\\r', ' ')
    text = text.replace('\\t', ' ')
    # remove punctuations
    text = text.translate(str.maketrans(' ', ' ', string.punctuation))
    text = text.lower()
    #text = text.replace('rn', ' ')
    return text


def GetMessage(service, user_id, msg_id):
  """Get a Message with given ID.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id).execute()

    return message
  except errors.HttpError:
    print('An error occurred: ')


def GetMimeMessage(service, user_id, msg_id, idx):
  """Get a Message and use it to create a MIME Message.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    msg_id: The ID of the Message required.

  Returns:
    A MIME Message, consisting of data from Message.
  """
  try:
    message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()

    msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))
    mail = mailparser.parse_from_bytes(msg_str)

    msg_str = str(mail.text_plain)
    msg_str = msg_str.strip("")
    msg_str = clean_text(msg_str)
    msg_str = preprocess(msg_str)

    #print(msg_str)

  except errors.HttpError:
    print('An error occurred:')

  try:
    met = service.users().messages().get(userId=user_id, id=msg_id, format='metadata').execute()

    pay = met['payload']
    head = pay['headers']
    sub=""
    for h in head:
      if (h['name'] == 'Subject'):
        sub = "Subject: "+str(h['value'])
  except errors.HttpError:
    print('An error occurred:')
  filename = "./ham/email"
  file_extension = ".txt"
  new_fname = "{}-{}{}".format(filename, idx, file_extension)
  #print(new_fname)
  f= open(new_fname,"w+")
  f.write(sub+"\n")
  f.write(msg_str)
  f.close()

def main():
    """Shows basic usage of the Gmail API.
    Lists the user's Gmail labels.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('gmail', 'v1', credentials=creds)

    # Call the Gmail API
    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    if not labels:
        print('No labels found.')
    else:
        print('Labels:')
        for label in labels:
            print(label['name'])
    path = "./ham"
    try:
        os.mkdir(path)
    except OSError:
        print ("Creation of the directory %s failed" % path)
    else:
        print ("Successfully created the directory %s " % path)

    messages = []
    messages = ListMessagesMatchingQuery(service, 'me', 'in:inbox')
    idx = 0
    for message in messages:
      GetMimeMessage(service, 'me', message['id'], idx)
      idx+=1


def ListMessagesMatchingQuery(service, user_id, query=''):
  """List all Messages of the user's mailbox matching the query.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    query: String used to filter messages returned.
    Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

  Returns:
    List of Messages that match the criteria of the query. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate ID to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError:
    print("An error occurred")


def ListMessagesWithLabels(service, user_id, label_ids=[]):
  """List all Messages of the user's mailbox with label_ids applied.

  Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
    can be used to indicate the authenticated user.
    label_ids: Only return Messages with these labelIds applied.

  Returns:
    List of Messages that have all required Labels applied. Note that the
    returned list contains Message IDs, you must use get with the
    appropriate id to get the details of a Message.
  """
  try:
    response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
    messages = []
    if 'messages' in response:
      messages.extend(response['messages'])

    while 'nextPageToken' in response:
      page_token = response['nextPageToken']
      response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
      messages.extend(response['messages'])

    return messages
  except errors.HttpError:
    print("An error occurred")

if __name__ == '__main__':
    main()
