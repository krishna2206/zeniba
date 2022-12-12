from dataclasses import dataclass
from typing import List, Optional

import tqdm

from zeniba.client import Client
from zeniba.parser import Parser


@dataclass
class Book:
    """Book metadata"""

    # ids
    zid: str
    did: str

    # meta
    title: str
    authors: List[str]
    cover: str
    categories: List[str]
    volume: int
    year: int
    edition: str
    publisher: str
    language: str
    pages: int
    isbn: str
    isbn_10: str
    isbn_13: str
    series: List[str]

    # TODO
    # description: List[str]

    def __post_init__(self):

        # adjust did (link -> did)
        self.did = self.did.replace("/dl/", "")


def download(client: Client, did: str, out: Optional[str] = None) -> str:
    """Book downloader"""

    response = client.get(f"/dl/{did}", stream=True)

    # TODO check if the pattern of the header is always the same
    content_disposition = response.headers["Content-Disposition"]
    filename = content_disposition.split(";filename*=")[0].replace(
        "attachment; filename=", ""
    )[1:-1]
    total_length = float(response.headers.get('content-length', 0))
    out = out or filename

    print(f"Downloading {filename} to {out}")
    with open(out, "wb") as file, tqdm.tqdm(
        total=total_length,
        unit='iB',
        unit_scale=True,
        unit_divisor=1024
    ) as pbar:
        for data in response.iter_content(chunk_size=4096):
            size = file.write(data)
            pbar.update(size)
    print(f"Downloaded {filename} to {out}")

    return f"{out}/{filename}"


def book(client: Client, zid: str):
    """Book handler"""

    page = client.get(f"/book/{zid}").text
    parser = Parser(page)

    return Book(
        zid=zid,
        did=parser.field("a.dlButton", "href")[0],
        title=parser.text_s('h1[itemprop="name"]'),
        authors=parser.text('a[itemprop="author"]'),
        cover=parser.field("div.z-book-cover > img", "src")[0],
        categories=parser.property("categories"),
        volume=parser.property("volume", mod=int, default="-1"),
        year=parser.property("year", mod=int, default="-1"),
        edition=parser.property("edition"),
        publisher=parser.property("publisher"),
        language=parser.property("language"),
        pages=parser.property("pages", mod=int, default="-1"),
        isbn=parser.property(r"isbn.\31 3 + .property_isbn"),
        isbn_10=parser.property(r"isbn.\31 0"),
        isbn_13=parser.property(r"isbn.\31 3"),
        series=parser.property("series"),
    )
