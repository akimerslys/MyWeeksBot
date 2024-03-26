import datetime

import aiohttp
import asyncio
from bs4 import BeautifulSoup
from python_utils import converters

HLTV_COOKIE_TIMEZONE = "UTC"

TEAM_MAP_FOR_RESULTS = []


async def get_parsed_page(url: str) -> BeautifulSoup:
    headers = {
        "referer": "https://www.hltv.org/stats",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    cookies = {
        "hltvTimeZone": HLTV_COOKIE_TIMEZONE
    }

    async with aiohttp.ClientSession(headers=headers, cookies=cookies) as session:
        async with session.get(url) as response:
            text = await response.text()
            return BeautifulSoup(text, "lxml")


async def get_matches():
    matches = await get_parsed_page("https://www.hltv.org/matches/")
    matches_list = []

    matchdays = matches.find_all("div", {"class": "upcomingMatchesSection"})

    for match in matchdays:
        matchDetails = match.find_all("div", {"class": "upcomingMatch"})
        date = match.find({'div': {'class': 'matchDayHeadline'}}).text.split()[-1]
        for getMatch in matchDetails:
            matchObj = {}

            matchObj['url'] = "https://hltv.org" + getMatch.find("a", {"class": "match a-reset"}).get("href")
            matchObj['match-id'] = converters.to_int(getMatch.find("a", {"class": "match a-reset"}).get("href").split("/")[-2])

            if (date and getMatch.find("div", {"class": "matchTime"})):
                timeFromHLTV = datetime.datetime.strptime(date + " " + getMatch.find("div", {"class": "matchTime"}).text,'%Y-%m-%d %H:%M').replace(tzinfo='UTC')
                matchObj['date'] = timeFromHLTV.strftime('%Y-%m-%d')
                matchObj['time'] = timeFromHLTV.strftime('%H:%M')

                #matchObj['countdown'] = _generate_countdown(date, getMatch.find("div", {"class": "matchTime"}).text)

                if not MATCH_WITH_COUNTDOWN and matchObj['countdown']:
                    MATCH_WITH_COUNTDOWN = converters.to_int(getMatch.find("a", {"class": "match a-reset"}).get("href").split("/")[-2])

            if getMatch.find("div", {"class": "matchEvent"}):
                matchObj['event'] = getMatch.find("div", {"class": "matchEvent"}).text.strip()
            else:
                matchObj['event'] = getMatch.find("div", {"class": "matchInfoEmpty"}).text.strip()

            if (getMatch.find_all("div", {"class": "matchTeams"})):
                matchObj['team1'] = getMatch.find_all("div", {"class": "matchTeam"})[0].text.lstrip().rstrip()
                matchObj['team1-id'] = await _findTeamId(getMatch.find_all("div", {"class": "matchTeam"})[0].text.lstrip().rstrip())
                matchObj['team2'] = getMatch.find_all("div", {"class": "matchTeam"})[1].text.lstrip().rstrip()
                matchObj['team2-id'] = await _findTeamId(getMatch.find_all("div", {"class": "matchTeam"})[1].text.lstrip().rstrip())
            else:
                matchObj['team1'] = None
                matchObj['team1-id'] = None
                matchObj['team2'] = None
                matchObj['team2-id'] = None

            matches_list.append(matchObj)

    return matches_list


async def _get_all_teams():
    global TEAM_MAP_FOR_RESULTS
    if not TEAM_MAP_FOR_RESULTS:
        teams = await get_parsed_page("https://www.hltv.org/stats/teams?minMapCount=0")
        for team in teams.find_all("td", {"class": ["teamCol-teams-overview"], }):
            team = {'id': converters.to_int(team.find("a")["href"].split("/")[-2]), 'name': team.find("a").text, 'url': "https://hltv.org" + team.find("a")["href"]}
            TEAM_MAP_FOR_RESULTS.append(team)


async def _findTeamId(teamName: str):
    await _get_all_teams()
    for team in TEAM_MAP_FOR_RESULTS:
        if team['name'] == teamName:
            return team['id']
    return None


async def main():
    page = await get_matches()

    with open('matches.json', 'w') as file:
        file.write(str(page))

if __name__ == "__main__":
    asyncio.run(main())