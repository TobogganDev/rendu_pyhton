import requests
import threading

class TEST():
  def __init__(self):
    self.session = requests.Session()
    self.base_url = 'https://4h368paqnk.execute-api.eu-west-3.amazonaws.com/dev'

  def get_user(self):
    try:
      res = self.session.get(
        url = f"{self.base_url}/manageUser"
      )
      res.raise_for_status()
      data = res.text
      print(data)
      return data
    except Exception as e:
      print(f"Error getting user: {str(e)}")


  def create_user (self, email):
    res = self.session.post(
      url = f'{self.base_url}/insertEmail',
      json = {
        "email": email
      }
    )
    res.raise_for_status()

    user_token = res.json()['token']
    print(user_token)

    self.session.headers.update({
      'user_token': user_token
    })

    return user_token
  

def create_user_thread(email):
  test = TEST()
  test.create_user(email)
  test.get_user()

emails = ["test1@test.com", "test2@test.com", "test3@test.com"]
threads = []

for email in emails:
  thread = threading.Thread(target=create_user_thread, args=(email,))
  threads.append(thread)
  thread.start()

for thread in threads:
  thread.join()