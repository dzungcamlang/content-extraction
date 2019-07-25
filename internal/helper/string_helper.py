# -*- coding: utf-8 -*-
import re
import json


class StringHelper:
    def __init__(self):
        pass

    # TODO: test more
    def replace_unclose_img_tag(self, html=''):
        return re.sub(r'(<img[^\>]*)(\>|\/\>)', r'\1/>', html)

    def replace_unclose_br_tag(self, html=''):
        return re.sub(r'(<br[^\>]*)(\>|\/\>)', r'\1/>', html)

    def replace_unclose_input_tag(self, html=''):
        return re.sub(r'(<input[^\>]*)(\>|\/\>)', r'\1/>', html)

    def replace_unclose_meta_tag(self, html=''):
        return re.sub(r'(<meta[^\>]*)(\>|\/\>)', r'\1/>', html)

    def get_obj_attr_str(self, object=None):
        attrs = vars(object)
        return ', '.join("%s: %s" % item for item in attrs.items())

    def convert_vietnamese_to_eng(self, utf8_str=''):
        try:
            INTAB = "ạảãàáâậầấẩẫăắằặẳẵóòọõỏôộổỗồốơờớợởỡéèẻẹẽêếềệểễúùụủũưựữửừứíìịỉĩýỳỷỵỹđẠẢÃÀÁÂẬẦẤẨẪĂẮẰẶẲẴÓÒỌÕỎÔỘỔỖỒỐƠỜỚỢỞỠÉÈẺẸẼÊẾỀỆỂỄÚÙỤỦŨƯỰỮỬỪỨÍÌỊỈĨÝỲỶỴỸĐ"
            INTAB = [ch for ch in INTAB]

            OUTTAB = "a" * 17 + "o" * 17 + "e" * 11 + "u" * 11 + "i" * 5 + "y" * 5 + "d" + "A" * 17 + "O" * 17 + "E" * 11 + "U" * 11 + "I" * 5 + "Y" * 5 + "D"

            r = re.compile("|".join(INTAB))
            replaces_dict = dict(zip(INTAB, OUTTAB))

            result = r.sub(lambda m: replaces_dict[m.group(0)], utf8_str)

        except UnicodeWarning:
            result = utf8_str

        return result

    def is_paragraph(self, paragraph=''):
        return True if (len(paragraph) > 20 and self.total_sentences(paragraph) >= 2) or len(paragraph) > 70 else False

    def total_sentences(self, paragraph=''):
        sentences = paragraph.split('.')
        total = 0
        for sentence in sentences:
            if sentence.strip() != '' and len(self.convert_vietnamese_to_eng(sentence.strip())) > 10:
                total += 1
        return total

    def is_int(self, txt=''):
        try:
            int(txt)
            return True
        except ValueError:
            return False

    def load_json(self, json_string=''):
        try:
            json_object = json.loads(json_string)
        except ValueError:
            return None

        return json_object

