# SPDX-License-Identifier: AGPL-3.0-or-later
# lint: pylint
"""DuckDuckGo Weather"""

from json import loads
from urllib.parse import quote

from datetime import datetime
from flask_babel import gettext

about = {
    "website": 'https://duckduckgo.com/',
    "wikidata_id": 'Q12805',
    "official_api_documentation": None,
    "use_official_api": True,
    "require_api_key": False,
    "results": "JSON",
}

categories = ["others"]

url = "https://duckduckgo.com/js/spice/forecast/{query}/{lang}"


def generate_condition_table(condition):
    res = ""

    res += f"<tr><td><b>{gettext('Condition')}</b></td>" f"<td><b>{condition['summary']}</b></td></tr>"

    res += (
        f"<tr><td><b>{gettext('Temperature')}</b></td>"
        f"<td><b>{f_to_c(condition['temperature'])}°C / {condition['temperature']}°F</b></td></tr>"
    )

    res += (
        f"<tr><td>{gettext('Feels like')}</td><td>{f_to_c(condition['apparentTemperature'])}°C / "
        f"{condition['apparentTemperature']}°F</td></tr>"
    )

    res += (
        f"<tr><td>{gettext('Wind')}</td><td>{condition['windBearing']}° — "
        f"{'%.2f' % (condition['windSpeed'] * 1.6093440006147)} km/h / {condition['windSpeed']} mph</td></tr>"
    )

    res += f"<tr><td>{gettext('Visibility')}</td><td>{condition['visibility']} km</td>"

    res += f"<tr><td>{gettext('Humidity')}</td><td>{condition['humidity'] * 100}%</td></tr>"

    return res


def generate_day_table(day):
    res = ""

    res += (
        f"<tr><td>{gettext('Min temp.')}</td><td>{f_to_c(day['temperatureLow'])}°C / "
        f"{day['temperatureLow']}°F</td></tr>"
    )
    res += (
        f"<tr><td>{gettext('Max temp.')}</td><td>{f_to_c(day['temperatureHigh'])}°C / "
        f"{day['temperatureHigh']}°F</td></tr>"
    )
    res += f"<tr><td>{gettext('UV index')}</td><td>{day['uvIndex']}</td></tr>"
    res += (
        f"<tr><td>{gettext('Sunrise')}</td><td>{datetime.fromtimestamp(day['sunriseTime']).strftime('%H:%M')}</td></tr>"
    )
    res += (
        f"<tr><td>{gettext('Sunset')}</td><td>{datetime.fromtimestamp(day['sunsetTime']).strftime('%H:%M')}</td></tr>"
    )

    return res


def request(query, params):
    params["url"] = url.format(query=quote(query), lang=params['language'].split('-')[0])

    return params


def f_to_c(temperature):
    return "%.2f" % ((temperature - 32) / 1.8)


def response(resp):
    results = []

    if resp.text.strip() == "ddg_spice_forecast();":
        return []

    result = loads(resp.text[resp.text.find('\n') + 1 : resp.text.rfind('\n') - 2])

    current = result["currently"]

    title = result['flags']['ddg-location']

    infobox = f"<h3>{gettext('Current condition')}</h3><table><tbody>"

    infobox += generate_condition_table(current)

    infobox += "</tbody></table>"

    last_date = None

    for time in result['hourly']['data']:
        current_time = datetime.fromtimestamp(time['time'])

        if last_date != current_time.date():
            if last_date is not None:
                infobox += "</tbody></table>"

            infobox += f"<h3>{current_time.strftime('%Y-%m-%d')}</h3>"

            infobox += "<table><tbody>"

            for day in result['daily']['data']:
                if datetime.fromtimestamp(day['time']).date() == current_time.date():
                    infobox += generate_day_table(day)

            infobox += "</tbody></table><table><tbody>"

        last_date = current_time.date()

        infobox += f"<tr><td rowspan=\"7\"><b>{current_time.strftime('%H:%M')}</b></td></tr>"

        infobox += generate_condition_table(time)

    infobox += "</tbody></table>"

    results.append(
        {
            "infobox": title,
            "content": infobox,
        }
    )

    return results
