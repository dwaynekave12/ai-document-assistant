from chunker import chunk_pages


def test_short_page_becomes_one_chunk():
    chunks = chunk_pages(["hello world"])

    assert len(chunks) == 1
    assert chunks[0].text == "hello world"
    assert chunks[0].page == 1


def test_empty_pages_are_skipped_but_page_numbers_are_kept():
    chunks = chunk_pages(["", "   ", "some text"])

    assert len(chunks) == 1
    assert chunks[0].page == 3


def test_long_page_is_split_with_overlap():
    words = [f"w{i}" for i in range(500)]
    chunks = chunk_pages([" ".join(words)], chunk_size=200, overlap=40)

    assert len(chunks) == 3
    # The last 40 words of one chunk are the first 40 of the next
    assert chunks[0].text.split()[-40:] == chunks[1].text.split()[:40]
    # Nothing is lost at the end
    assert chunks[-1].text.split()[-1] == "w499"


def test_chunks_never_cross_pages():
    chunks = chunk_pages(["page one text", "page two text"])

    assert [chunk.page for chunk in chunks] == [1, 2]