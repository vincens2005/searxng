from flask_babel import gettext

keywords = ('ip', 'address',)

# required answerer function
# can return a list of results (any result type) for a given query
def answer(_, request):
    return [{'answer': request.remote_addr}]


# required answerer function
# returns information about the answerer
def self_info():
    return {
        'name': gettext('IP Address'),
        'description': gettext('Returns your IP address.'),
        'examples': ['ip'],
    }
