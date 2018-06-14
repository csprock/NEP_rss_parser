import re

def process_results(results):
    """
    Applies the format_doc() function over the results of an articleAPI.search() call.
    
    Input
    -----
    requests packet returned by searchAPI.
    
    Returns
    -------
    data_list: list of dict
        list of dictionaries containing fields returned by articleAPI object parsed by format_doc()
    """
    
    data_list = list()
    
    for d in results['response']['docs']:     # extract from requests packet
        data_list.append(format_doc(d))
        
    return data_list


def format_doc(article): 
    """
    This function extracts fields returned by the articleAPI object. Applies regex functions on some fields. 
    Error handling for missing fields. Parses keywords and bylines converting into lists. 
    
    Extracts the following fields:        
    
    Input
    -----
    article: dict
        dictionary of results returned in the resquests packet that is returned by the articleAPI.search() call.
    
    Output
    ------
    document: dict
        dictionary containing extracted fields
        
    """
    
    def _extract_keywords(keywords):
        # converts keyword dictionaries to tuples
        output = list()
        for kw in keywords:
            
            value = kw['value']
            if value.isupper():
                value = value.title()
            
            output.append((kw['name'], value))
            
        return output
        

    def _extract_authors(byline):
        # extract author names, applies regex filters 
        byline = byline.title()
        byline = re.sub('And |and ', ',', re.sub('By |Por ','', byline)).split(',')
        name_list = []
        for s in byline:
            if len(s) > 1:
                name_list.append(s.strip())
            
        return name_list

    
    document = dict()
    
    document['id'] = article['_id']
    document['type'] = article['document_type']
    document['url'] = article['web_url']
    document['date'] = article['pub_date'].split("T")[0]    # extract date part from date/time stamp


    
    try:
        document['keywords'] = _extract_keywords(article['keywords'])
    except:
        document['keywords'] = None
        
    
    # headline
    try:
        document['headline'] = article['headline']['main']
    except KeyError:
        document['headline'] = None
    
    # material
    try:
        document['material'] = article['type_of_material']
    except KeyError:
        document['material'] = None
        
    # source
    try:
        document['source'] = article['source']
    except KeyError:
        document['source'] = None
    
#    # byline
#    try:
#        document['original'] = _extract_authors(article['byline']['original'])
#    except TypeError:
#        document['original'] = None
#    except KeyError:
#        document['original'] = None

    # lead paragraph
    try:
        document['lead_paragraph'] = article['lead_paragraph']
    except KeyError:
        document['lead_paragraph'] = None
    
    # abstract
    try:
        document['abstract'] = re.sub('<.*?>', '', article['abstract'])
    except KeyError:
        document['abstract'] = None
                
    # snippet
    try:
        document['snippet'] = re.sub('<.*?>', '', article['snippet'])
    except KeyError:
        document['snippet'] = None
                
    # desk
    if 'news_desk' in article.keys():
        document['desk'] = article['news_desk']
    elif 'new_desk' in article.keys():
        document['desk'] = article['new_desk']
    else:
        document['desk'] = None
                
    # page
    try:
        document['page'] = int(article['print_page'])
    except:
        document['page'] = None
                
    # word count        
    try:
        document['word_count'] = int(article['word_count'])
    except:
        document['word_count'] = None
                
    # section
    try:
        document['section'] = article['section_name']
    except KeyError:
        document['section'] = None
                
    # subsection
    try:
        document['subsection'] = article['subsection_name']
    except KeyError:
        document['subsection'] = None
                        
    return document