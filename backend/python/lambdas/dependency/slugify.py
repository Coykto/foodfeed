import re

char_map = {
    "Ä°": "I", "Âª": "a", "Âº": "o", "ÃŸ": "ss", "áºž": "SS", "Ã€": "A", "Ã": "a", "Ã": "A", "Ã¡": "a", "Ã‚": "A",
    "Ã¢": "a", "Ãƒ": "A", "Ã£": "a", "Ã„": "A", "Ã¤": "a", "Ã…": "A", "Ã¥": "a", "Ã†": "AE", "Ã¦": "ae", "Ã‡": "C",
    "Ã§": "c", "Ãˆ": "E", "Ã¨": "e", "Ã‰": "E", "Ã©": "e", "ÃŠ": "E", "Ãª": "e", "Ã‹": "E", "Ã«": "e", "ÃŒ": "I",
    "Ã¬": "i", "Ã": "I", "Ã­": "i", "ÃŽ": "I", "Ã®": "i", "Ã": "I", "Ã¯": "i", "Ã": "D", "Ã°": "d", "Ã‘": "N",
    "Ã±": "n", "Ã’": "O", "Ã²": "o", "Ã“": "O", "Ã³": "o", "Ã”": "O", "Ã´": "o", "Ã•": "O", "Ãµ": "o", "Ã–": "O",
    "Ã¶": "o", "Ã˜": "O", "Ã¸": "o", "Ã™": "U", "Ã¹": "u", "Ãš": "U", "Ãº": "u", "Ã›": "U", "Ã»": "u", "Ãœ": "U",
    "Ã¼": "u", "Ã": "Y", "Ã½": "y", "Ãž": "TH", "Ã¾": "th", "Ã¿": "y", "Å¸": "Y", "Ä€": "A", "Ä": "a", "Ä‚": "A",
    "Äƒ": "a", "Ä„": "A", "Ä…": "a", "Ä†": "C", "Ä‡": "c", "ÄŒ": "C", "Ä": "c", "ÄŽ": "D", "Ä": "d", "Ä": "DJ",
    "Ä‘": "dj", "Ä’": "E", "Ä“": "e", "Ä–": "E", "Ä—": "e", "Ä˜": "e", "Ä™": "e", "Äš": "E", "Ä›": "e", "Äž": "G",
    "ÄŸ": "g", "Ä¢": "G", "Ä£": "g", "Ä¨": "I", "Ä©": "i", "Äª": "i", "Ä«": "i", "Ä®": "I", "Ä¯": "i", "Ä±": "i",
    "Ä¶": "k", "Ä·": "k", "Ä»": "L", "Ä¼": "l", "Ä½": "L", "Ä¾": "l", "Å": "L", "Å‚": "l", "Åƒ": "N", "Å„": "n",
    "Å…": "N", "Å†": "n", "Å‡": "N", "Åˆ": "n", "ÅŒ": "O", "Å": "o", "Å": "O", "Å‘": "o", "Å’": "OE", "Å“": "oe",
    "Å”": "R", "Å•": "r", "Å˜": "R", "Å™": "r", "Åš": "S", "Å›": "s", "Åž": "S", "ÅŸ": "s", "Å": "S", "Å¡": "s",
    "Å¢": "T", "Å£": "t", "Å¤": "T", "Å¥": "t", "Å¨": "U", "Å©": "u", "Åª": "u", "Å«": "u", "Å®": "U", "Å¯": "u",
    "Å°": "U", "Å±": "u", "Å²": "U", "Å³": "u", "Å´": "W", "Åµ": "w", "Å¶": "Y", "Å·": "y", "Å¹": "Z", "Åº": "z",
    "Å»": "Z", "Å¼": "z", "Å½": "Z", "Å¾": "z", "Æ’": "f", "Æ": "O", "Æ¡": "o", "Æ¯": "U", "Æ°": "u", "Çˆ": "LJ",
    "Ç‰": "lj", "Ç‹": "NJ", "ÇŒ": "nj", "È˜": "S", "È™": "s", "Èš": "T", "È›": "t", "Æ": "E", "É™": "e", "Ëš": "o",
    "Î": "i", "Î†": "A", "Î¬": "a", "Îˆ": "E", "Î­": "e", "Î‰": "H", "Î®": "h", "ÎŠ": "I", "Î¯": "i", "Î°": "y",
    "Î‘": "A", "Î±": "a", "Î’": "B", "Î²": "b", "Î“": "G", "Î³": "g", "Î”": "D", "Î´": "d", "Î•": "E", "Îµ": "e",
    "Î–": "Z", "Î¶": "z", "Î—": "H", "Î·": "h", "Î˜": "8", "Î¸": "8", "Î™": "I", "Î¹": "i", "Îš": "K", "Îº": "k",
    "Î›": "L", "Î»": "l", "Îœ": "M", "Î¼": "m", "Î": "N", "Î½": "n", "Îž": "3", "Î¾": "3", "ÎŸ": "O", "Î¿": "o",
    "Î": "P", "Ï€": "p", "Î¡": "R", "Ï": "r", "Ï‚": "s", "Î£": "S", "Ïƒ": "s", "Î¤": "T", "Ï„": "t", "Î¥": "Y",
    "Ï…": "y", "Î¦": "F", "Ï†": "f", "Î§": "X", "Ï‡": "x", "Î¨": "PS", "Ïˆ": "ps", "Î©": "W", "Ï‰": "w", "Îª": "I",
    "ÏŠ": "i", "Î«": "Y", "Ï‹": "y", "ÎŒ": "O", "ÏŒ": "o", "ÎŽ": "Y", "Ï": "y", "Î": "W", "ÏŽ": "w", "Ð": "A",
    "Ð°": "a", "Ð‘": "B", "Ð±": "b", "Ð’": "V", "Ð²": "v", "Ð“": "G", "Ð³": "g", "Ð”": "D", "Ð´": "d", "Ð•": "E",
    "Ðµ": "e", "Ð–": "Zh", "Ð¶": "zh", "Ð—": "Z", "Ð·": "z", "Ð˜": "I", "Ð¸": "i", "Ð™": "J", "Ð¹": "j", "Ðš": "K",
    "Ðº": "k", "Ð›": "L", "Ð»": "l", "Ðœ": "M", "Ð¼": "m", "Ð": "N", "Ð½": "n", "Ðž": "O", "Ð¾": "o", "ÐŸ": "P",
    "Ð¿": "p", "Ð": "R", "Ñ€": "r", "Ð¡": "S", "Ñ": "s", "Ð¢": "T", "Ñ‚": "t", "Ð£": "U", "Ñƒ": "u", "Ð¤": "F",
    "Ñ„": "f", "Ð¥": "H", "Ñ…": "h", "Ð¦": "C", "Ñ†": "c", "Ð§": "Ch", "Ñ‡": "ch", "Ð¨": "Sh", "Ñˆ": "sh", "Ð©": "Sh",
    "Ñ‰": "sh", "Ðª": "U", "ÑŠ": "u", "Ð«": "Y", "Ñ‹": "y", "Ð¬": "", "ÑŒ": "", "Ð­": "E", "Ñ": "e", "Ð®": "Yu",
    "ÑŽ": "yu", "Ð¯": "Ya", "Ñ": "ya", "Ð": "Yo", "Ñ‘": "yo", "Ð‚": "DJ", "Ñ’": "dj", "Ð„": "Ye", "Ñ”": "ye",
    "Ð†": "I", "Ñ–": "i", "Ð‡": "Yi", "Ñ—": "yi", "Ðˆ": "J", "Ñ˜": "j", "Ð‰": "LJ", "Ñ™": "lj", "ÐŠ": "NJ", "Ñš": "nj",
    "Ð‹": "C", "Ñ›": "c", "Ñ": "u", "Ð": "DZ", "ÑŸ": "dz", "Ò": "G", "Ò‘": "g", "Ò’": "GH", "Ò“": "gh",
    "Òš": "KH", "Ò›": "kh", "Ò¢": "NG", "Ò£": "ng", "Ò®": "UE", "Ò¯": "ue", "Ò°": "U", "Ò±": "u", "Òº": "H", "Ò»": "h",
    "Ó˜": "AE", "Ó™": "ae", "Ó¨": "OE", "Ó©": "oe", "Ô±": "A", "Ô²": "B", "Ô³": "G", "Ô´": "D", "Ôµ": "E", "Ô¶": "Z",
    "Ô·": "E'", "Ô¸": "Y'", "Ô¹": "T'", "Ôº": "JH", "Ô»": "I", "Ô¼": "L", "Ô½": "X", "Ô¾": "C'", "Ô¿": "K", "Õ€": "H",
    "Õ": "D'", "Õ‚": "GH", "Õƒ": "TW", "Õ„": "M", "Õ…": "Y", "Õ†": "N", "Õ‡": "SH", "Õ‰": "CH", "ÕŠ": "P", "Õ‹": "J",
    "ÕŒ": "R'", "Õ": "S", "ÕŽ": "V", "Õ": "T", "Õ": "R", "Õ‘": "C", "Õ“": "P'", "Õ”": "Q'", "Õ•": "O''",
    "Õ–": "F", "Ö‡": "EV", "Ø¡": "a", "Ø¢": "aa", "Ø£": "a", "Ø¤": "u", "Ø¥": "i", "Ø¦": "e", "Ø§": "a", "Ø¨": "b",
    "Ø©": "h", "Øª": "t", "Ø«": "th", "Ø¬": "j", "Ø­": "h", "Ø®": "kh", "Ø¯": "d", "Ø°": "th", "Ø±": "r", "Ø²": "z",
    "Ø³": "s", "Ø´": "sh", "Øµ": "s", "Ø¶": "dh", "Ø·": "t", "Ø¸": "z", "Ø¹": "a", "Øº": "gh", "Ù": "f", "Ù‚": "q",
    "Ùƒ": "k", "Ù„": "l", "Ù…": "m", "Ù†": "n", "Ù‡": "h", "Ùˆ": "w", "Ù‰": "a", "ÙŠ": "y", "Ù‹": "an", "ÙŒ": "on",
    "Ù": "en", "ÙŽ": "a", "Ù": "u", "Ù": "e", "Ù’": "", "Ù ": "0", "Ù¡": "1", "Ù¢": "2", "Ù£": "3", "Ù¤": "4",
    "Ù¥": "5", "Ù¦": "6", "Ù§": "7", "Ù¨": "8", "Ù©": "9", "Ù¾": "p", "Ú†": "ch", "Ú˜": "zh", "Ú©": "k", "Ú¯": "g",
    "ÛŒ": "y", "Û°": "0", "Û±": "1", "Û²": "2", "Û³": "3", "Û´": "4", "Ûµ": "5", "Û¶": "6", "Û·": "7", "Û¸": "8",
    "Û¹": "9", "áƒ": "a", "áƒ‘": "b", "áƒ’": "g", "áƒ“": "d", "áƒ”": "e", "áƒ•": "v", "áƒ–": "z", "áƒ—": "t",
    "áƒ˜": "i", "áƒ™": "k", "áƒš": "l", "áƒ›": "m", "áƒœ": "n", "áƒ": "o", "áƒž": "p", "áƒŸ": "zh", "áƒ": "r",
    "áƒ¡": "s", "áƒ¢": "t", "áƒ£": "u", "áƒ¤": "f", "áƒ¥": "k", "áƒ¦": "gh", "áƒ§": "q", "áƒ¨": "sh", "áƒ©": "ch",
    "áƒª": "ts", "áƒ«": "dz", "áƒ¬": "ts", "áƒ­": "ch", "áƒ®": "kh", "áƒ¯": "j", "áƒ°": "h", "áº€": "W", "áº": "w",
    "áº‚": "W", "áºƒ": "w", "áº„": "W", "áº…": "w", "áº": "A", "áº¡": "a", "áº¢": "A", "áº£": "a", "áº¤": "A",
    "áº¥": "a", "áº¦": "A", "áº§": "a", "áº¨": "A", "áº©": "a", "áºª": "A", "áº«": "a", "áº¬": "A", "áº­": "a",
    "áº®": "A", "áº¯": "a", "áº°": "A", "áº±": "a", "áº²": "A", "áº³": "a", "áº´": "A", "áºµ": "a", "áº¶": "A",
    "áº·": "a", "áº¸": "E", "áº¹": "e", "áºº": "E", "áº»": "e", "áº¼": "E", "áº½": "e", "áº¾": "E", "áº¿": "e",
    "á»€": "E", "á»": "e", "á»‚": "E", "á» ƒ": "e", "á»„": "E", "á»…": "e", "á»†": "E", "á»‡": "e", "á» ˆ": "I",
    "á»‰": "i", "á» Š": "I", "á»‹": "i", "á» Œ": "O", "á»": "o", "á» Ž": "O", "á»": "o", "á»": "O", "á»‘": "o",
    "á»’": "O", "á»“": "o", "á»”": "O", "á»•": "o", "á»–": "O", "á»—": "o", "á»˜": "O", "á»™": "o", "á» š": "O",
    "á»›": "o", "á» œ": "O", "á»": "o", "á» ž": "O", "á» Ÿ": "o", "á»": "O", "á»¡": "o", "á»¢": "O", "á»£": "o",
    "á»¤": "U", "á»¥": "u", "á»¦": "U", "á»§": "u", "á»¨": "U", "á»©": "u", "á» ª": "U", "á»«": "u", "á»¬": "U",
    "á»­": "u", "á»®": "U", "á»¯": "u", "á»°": "U", "á»±": "u", "á»²": "Y", "á»³": "y", "á»´": "Y", "á» µ": "y",
    "á»¶": "Y", "á»·": "y", "á»¸": "Y", "á»¹": "y", "â€“": "-", "â€˜": "'", "â€™": "'", "â€œ": '"', "â€": '"',
    "â€ž": '"', "â€ ": "+", "â€¢": "*", "â€¦": "..."
}


def replace_chars(text):
    for k, v in char_map.items():
        text = text.replace(k, v)
    return text


def slugify(item_name):
    # Replace special characters
    item_name = replace_chars(item_name)

    # Remove non-ASCII characters
    item_name = re.sub(r'[^\x20-\x7F]+', '', item_name)

    # Replace non-word characters or underscores with hyphens
    item_name = re.sub(r'(\W|_)+', '-', item_name)

    # Normalize hyphens
    item_name = re.sub(r'(^-+)|(-+$)|(-{2,})', '', item_name)

    # Convert to lowercase
    return item_name.lower()


def slug(item_name: str, item_id: str):
    return f"{slugify(item_name)}-itemid-{item_id}"