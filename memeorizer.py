"""
For your homework this week, you'll be creating a new WSGI application.

The MEMEORIZER acquires a phrase from one of two sources, and applies it
to one of two meme images.

The two possible sources are:

  1. A fact from http://unkno.com
  2. One of the 'Top Stories' headlines from http://www.cnn.com

For the CNN headline you can use either the current FIRST headline, or
a random headline from the list. I suggest starting by serving the FIRST
headline and then modifying it later if you want to.

The two possible meme images are:

  1. The Buzz/Woody X, X Everywhere meme
  2. The Ancient Aliens meme (eg https://memegenerator.net/instance/11837275)

To begin, you will need to collect some information. Go to the Ancient
Aliens meme linked above. Open your browser's network inspector; in Chrome
this is Ctrl-Shift-J and then click on the network tab. Try typing in some
new 'Bottom Text' and observe the network requests being made, and note
the imageID for the Ancient Aliens meme.

TODO #1:
The imageID for the Ancient Aliens meme is:

You will also need a way to identify headlines on the CNN page using
BeautifulSoup. On the 'Unnecessary Knowledge Page', our fact was
wrapped like so:

```
<div id="content">
  Penguins look like they're wearing tuxedos.
</div>
```

So our facts were identified by the tag having
* name: div
* attribute name: id
* attribute value: content.

We used the following BeautifulSoup call to isolate that element:

```
element = parsed.find('div', id='content')
```

Now we have to figure out how to isolate CNN headlines. Go to cnn.com and
'inspect' one of the 'Top Stories' headlines. In Chrome, you can right
click on a headline and click 'Inspect'. If an element has a rightward
pointing arrow, then you can click on it to see its contents.

TODO #2:
Each 'Top Stories' headline is wrapped in a tag that has:
* name:
* attribute name:
* attribute value:

NOTE: We used the `find` method to find our fact element from unkno.com.
The `find` method WILL ALSO work for finding a headline element from cnn.com,
although it will return exactly one headline element. That's enough to
complete the assignment, but if you want to isolate more than one headline
element you can use the `find_all` method instead.


TODO #3:
You will need to support the following four requests:

```
  http://localhost:8080/fact/buzz
  http://localhost:8080/fact/aliens
  http://localhost:8080/news/buzz
  http://localhost:8080/news/aliens
```

You can accomplish this by modifying the memefacter.py that we created
in class.

There are multiple ways to architect this assignment! You will probably
have to either change existing functions to take more arguments or create
entirely new functions.

I have started the assignment off by passing `path` into `process` and
breaking it apart using `strip` and `split` on lines 136, 118, and 120.

To submit your homework:

  * Fork this repository (PyWeb-04).
  * Edit this file to meet the homework requirements.
  * Your script should be runnable using `$ python memeorizer.py`
  * When the script is running, I should be able to view your
    application in my browser.
  * Commit and push your changes to your fork.
  * Submit a link to your PyWeb-04 fork repository!

"""

from bs4 import BeautifulSoup
import requests, html5lib

# Possible message types
FACT = 'fact'
NEWS_HEADLINES = 'news'

# Possible meme image options
BUZZ = 'buzz'  # the Buzz/Woody X, X Everywhere meme
ALIENS = 'aliens'  # The Ancient Aliens meme

# Image IDs
BUZZ_IMAGE_ID = 2097248  # the Buzz/Woody X, X Everywhere meme
ALIENS_IMAGE_ID = 627067  # the Ancient Aliens meme


def meme_it(image_type, fact):
    url = 'http://cdn.meme.am/Instance/Preview'

    if image_type == BUZZ:
        image_id = BUZZ_IMAGE_ID  # the Buzz/Woody X, X Everywhere meme
    elif image_type == ALIENS:
        image_id = ALIENS_IMAGE_ID  # the Ancient Aliens meme
    else:
        raise NameError  # invalid image type

    params = {
        'imageID': image_id,
        'text1': fact
    }

    response = requests.get(url, params)

    return response.content


def parse_fact(message_type, body):
    """
    Gets the fact or news headline from the given body of the page.

    :param message_type: the message type which can be fact or news
    :param body: the body of the message to be parsed
    :return: the fact from http://unkno.com or the news headline from http://www.cnn.com
    """

    parsed = BeautifulSoup(body, 'html5lib')

    if message_type == FACT:
        message = parsed.find('div', attrs={'id': 'content'})
    elif message_type == NEWS_HEADLINES:
        message = parsed.find('span', attrs={'class': 'cd__headline-text'})
    else:
        raise NameError # Invalid message type

    return message.text.strip()


def get_fact(message_type):
    """
    Gets the text message based on the message type, whioh can be fact or news.

    :param message_type: the message type can be 'fact' or 'news'
    :return: the text message of the fact or news
    """

    if message_type == FACT:
        response = requests.get('http://unkno.com')
    elif message_type == NEWS_HEADLINES:
        response = requests.get('http://www.cnn.com')
    else:
        raise NameError # Invalid message type
    return parse_fact(message_type, response.text)


def process(path):
    """
    Processes the URI and returns the meme.

    :param path: the URI
    :return: the meme
    """

    args = path.strip("/").split("/")


    # Make sure that the URI has the proper number of arguments, which can be one of the followings:
    #   fact/buzz
    #   fact/aliens
    #   news/buzz
    #   news/aliens
    if len(args) == 2:
        message = get_fact(args[0])  # Get the message from the fact or news web page.
        meme = meme_it(args[1], message)  # Meme the message on either the buzz or aliens image.
        return meme
    else:
        raise NameError  # Invalid operation


def application(environ, start_response):
    """
    Runs the server side application.

    :param environ: the environment information from the request
    :param start_response: the callable function that starts an HTTP response, sending status and headers
    :return: the body of the message to be sent to the client
    """
    headers = [('Content-type', 'image/jpeg')]
    try:
        # Get the URI.
        path = environ.get('PATH_INFO', None)
        if path is None:
            raise NameError

        # Process the URI request and obtain the image and the bottom text.
        body = process(path)
        status = "200 OK"
    except NameError:
        status = "404 Not Found"
        body = b"<h1>Not Found</h1>"
    except Exception:
        status = "500 Internal Server Error"
        body = b"<h1> Internal Server Error</h1>"
    finally:
        # Send the response back to the client.
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        return [body]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    srv = make_server('localhost', 8080, application)
    srv.serve_forever()
