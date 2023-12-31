import re
from html import unescape
from pathlib import Path

import requests
from fire import Fire

from utils.logging import get_logger

logger = get_logger("asp")


def load_html(path: Path) -> str:
    with open(path, "r") as f:
        return f.read()


# Note, the plotly-latest.min.js is linking to an old version as of 2023-12-30
# Fetch the latest version and use it instead
# For this fetch the version number from github's release page -> there are
# only zip files which I do not want to download and unzip
def add_plotlyjs(
    html: str, path: Path | None = None, embed: bool = False
) -> str:
    """Add plotly.js to the html file

    Parameters
    ----------
    html : str
        html text of the presentations index.html file

    path : Path | None
        path to the index.html file. Needed if `embed` is False to store the
        plotly.js file under the dist/ folder

    embed : bool
        whether to embed the plotly.js file into the html file or not. If false
        the plotly.js file is stored under the dist/ folder


    Returns
    -------
    str
        html text with plotly.js added

    """
    logger.debug("Fetching latest plotly version")
    version = fetch_latest_plotly()
    logger.debug(f"Latest version is {version}")

    if embed:
        logger.debug("Embedding plotly.js")
        return re.sub(
            r"<head>",
            r"<head>\n<script>"
            + requests.get(f"https://cdn.plot.ly/plotly-{version}.min.js").text
            + "</script>",
            html,
        )
    # store under the dist/ folder
    else:
        logger.debug("Saving plotly.js to ./dist")
        open(path.joinpath(f"./dist/plotly-{version}.min.js"), "w").write(
            requests.get(f"https://cdn.plot.ly/plotly-{version}.min.js").text
        )

        return re.sub(
            r"<head>",
            rf'<head>\n<script src="dist/plotly-{version}.min.js"></script>',
            html,
        )


def replace_images_with_html(
    html: str, plotly_html_path_prefix: Path = Path(".")
) -> str:
    """Replace all images with a preceding comment of `asp:/some/dir/to/html`
    with the according content of the html file. It is assumed that this file
    is a stored version of a plotly figure. The figure is then stripped for a
    bare minimum of the figure data itself.

    Parameters
    ----------
    html : str
        html text of the presentations index.html file

    plotly_html_path_prefix : Path
        path prefix to the html files, defaults to './'

    Returns
    -------
    str
        html text with images replaced with html content

    """

    matches = re.findall("(<!-- asp:.*\.html -->)[\n\s]*(<img .*>)", html)
    for cmnt, img in matches:
        path = plotly_html_path_prefix.joinpath(
            Path(cmnt.split(":")[1].strip().strip(" -->"))
        )
        if not path.exists():
            logger.warning(
                f"Could not find {path}. Continue without replacement"
            )
        else:
            div, script = extract_plotly_html(path)
            html = html.replace(
                img, div
            )  # use plain replace as with re.sub, some escape sequences are problematic
            html = html.replace("</body>", f"{script}\n</body>")

    return html


def extract_plotly_html(path: Path) -> tuple[str, str]:
    """
    From a plotly html file, extract the figure div and separate the script
    generating the figure.
    """

    html = re.search(
        r'(<div .* class="plotly-graph.*>.*</script>)\s*</div>',
        load_html(path),
        re.DOTALL,
    ).group(1)
    div = re.search(r"<div.*>.*</div>", html).group(0)
    script = re.search(r"<script.*>.*</script>", html).group(0)

    # the relevant parts if generated from a plotly json would look like this:
    # fdiv = """
    # <div {s} id='{chart_id}'></div>
    #             <script>var Plotjson = '{j}';
    #             var figure = JSON.parse(Plotjson);
    #             Plotly.newPlot('{chart_id}', figure.data, figure.layout);</script>"""
    #
    #

    return div, script


def fetch_latest_plotly() -> str:
    release_page = requests.get(
        "https://github.com/plotly/plotly.js/releases"
    ).text
    version = re.search(r"v\d+\.\d+\.\d+", release_page).group(0)
    return version[1:]


def process_index(path: Path, plotly_html_path_prefix: Path = Path(".")):
    logger.debug("Loading html")
    html = load_html(path)

    logger.debug("adding plotly.js")
    html = add_plotlyjs(html, path.parent, embed=False)

    logger.debug("replacing images")
    html = replace_images_with_html(
        html, plotly_html_path_prefix=plotly_html_path_prefix
    )

    # get rid of escape sequences
    logger.debug("Unescaping")
    html = unescape(html)

    logger.debug("writing out embedded html")
    open(path.parent.joinpath("index_embedded.html"), "w").write(html)


if __name__ == "__main__":
    Fire(process_index)
    logger.setLevel(10)

    # html = load_html(Path("./example_export/TestPresentation/index.html"))
    # path = Path("./example_export/behavioral_plots_comparison.html")
