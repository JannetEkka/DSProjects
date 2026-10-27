from chithi.meta import parse_sam


def test_parse_boxes_from_the_docs_format():
    text = "<0f>0<|box;x1=181;y1=365;x2=556;y2=486;w=1516;h=1600|><|mask;x=0;y=0;data=122,376,~abc|>"
    [b] = parse_sam(text, "table")
    assert (b.x1, b.y1, b.x2, b.y2, b.w, b.h, b.score) == (181, 365, 556, 486, 1516, 1600, None)


def test_parse_several_with_confidence():
    text = ("<0f>0<|box;x1=1;y1=2;x2=3;y2=4;w=10;h=10;c=0.91|><|mask;c=0.8;data=1,1,!x|>,"
            "1<|box;x1=5;y1=6;x2=7;y2=8;w=10;h=10;c=0.42|><|mask;data=1,1,!y|>")
    boxes = parse_sam(text, "stamp")
    assert [b.score for b in boxes] == [0.91, 0.42]


def test_no_match_is_empty():
    assert parse_sam("", "stamp") == []
