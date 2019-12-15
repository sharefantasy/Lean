from quantconnect import api

userId = 75490
token = "13babea8055915a623139dabb00213155dc5a597c8ea49724155d026aaa4085d"

if __name__ == "__main__":
    cli = api.Api(userId, token)
    cli.list_projects()
