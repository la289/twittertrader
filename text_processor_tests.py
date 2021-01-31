from text_processor import text_processor

text_pro = text_processor()

def test_find_tickers_1():
    assert text_pro.find_tickers("I have no ticker beach") == set()

def test_find_tickers_2():
    assert text_pro.find_tickers("I have 1 ticker $TSLA") == set(["$TSLA"])

def test_find_tickers_3():
    assert text_pro.find_tickers("$DOLLA DOLLA BILLS YO") == set()

def test_find_tickers_4():
    assert text_pro.find_tickers("") == set()

def test_find_tickers_5():
    assert text_pro.find_tickers("$TSLA $APPL $ETH $ETH $MSFT $GOOG$GOOG") == set(["$TSLA", "$APPL", "$ETH", "$MSFT"])

def test_get_company_name_1():
    assert text_pro.get_company_name("$TSLA") == "Tesla, Inc."

def test_get_company_name_2():
    assert text_pro.get_company_name("$AAPL") == "Apple Inc."

def test_get_company_name_4():
    assert text_pro.get_company_name("$GOOG") == "Alphabet Inc."

def test_get_company_name_5():
    assert text_pro.get_company_name("$ETH") == "Ethereum"

def test_get_company_name_5():
    assert text_pro.get_company_name("$") == "$"

def test_get_company_name_6():
    assert text_pro.get_company_name("") == ""

def test_get_company_name_7():
    assert text_pro.get_company_name("Not a ticker") == "Not a ticker"

def test_convert_tickers_to_company_names_1():
    assert text_pro.convert_tickers_to_company_names(["Not a ticker"]) == {}

def test_convert_tickers_to_company_names_2():
    assert text_pro.convert_tickers_to_company_names(["$TSLA"]) == {'$TSLA': 'Tesla, Inc.'}

def test_convert_tickers_to_company_names_3():
    assert text_pro.convert_tickers_to_company_names([]) == {}

def test_convert_tickers_to_company_names_4():
    assert text_pro.convert_tickers_to_company_names(['GOOG','$MSFT','$GNUS']) == {'$GNUS': 'Genius Brands International, Inc.', '$MSFT': 'Microsoft Corporation'}

def test_replace_tickers_with_company_names_1():
    assert text_pro.replace_tickers_with_company_names("") == ""

def test_replace_tickers_with_company_names_2():
    assert text_pro.replace_tickers_with_company_names("I like $GOOG") == "I like Alphabet Inc."

def test_replace_tickers_with_company_names_3():
    assert text_pro.replace_tickers_with_company_names("$MSFT I like $GOOG") == "Microsoft Corporation I like Alphabet Inc."

def test_replace_tickers_with_company_names_4():
    assert text_pro.replace_tickers_with_company_names("Wrist happened?  Did everyone sell their $ETH into $DOGE?") == "Wrist happened?  Did everyone sell their Ethereum into Dogecoin?"

def test_replace_tickers_with_company_names_5():
    assert text_pro.replace_tickers_with_company_names("Wrist happened? $ETH!! ROCKS!!Did everyone sell their $ETH into $DOGE?") == "Wrist happened? Ethereum!! ROCKS!!Did everyone sell their Ethereum into Dogecoin?"
