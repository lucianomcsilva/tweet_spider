import scrapy
from dotenv import load_dotenv
import tweepy
import string
import sys
import os
import pprint 
import json
import datetime

load_dotenv()
consumer_key    = os.environ['TWITTER_APIKEY']
consumer_secret = os.environ['TWITTER_APISECRET']

pp = pprint.PrettyPrinter(indent=4)

''' ------------------------------------------------------------------------------------  '''
''' -----------------------------  Simple log in colors --------------------------------  '''
''' ------------------------------------------------------------------------------------  '''
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_warning(str): 
    print(bcolors.WARNING + str + bcolors.ENDC)        

def print_error(str): 
    print(bcolors.FAIL + str + bcolors.ENDC)        

def print_info(str): 
    print(bcolors.OKCYAN + str + bcolors.ENDC)   

def print_sucess(str): 
    print(bcolors.OKGREEN + str + bcolors.ENDC)   
''' ------------------------------------------------------------------------------------  '''
''' ------------------------------------------------------------------------------------  '''

def removeDisallowedFilenameChars(filename):
    validFilenameChars = "-_.() %s%s" % (string.ascii_letters, string.digits)
    # cleanedFilename = unicodedata.normalize('NFKD', filename).encode('ASCII', 'ignore')
    return ''.join(c for c in filename if c in validFilenameChars)

def create_dir(domain, override):        
    path = domain
    if not os.path.exists(path):
        os.mkdir(path)
        os.mkdir(path+'/html')
    elif not override:
        i = 2
        while os.path.exists(path):
            path = domain + f" ({i})"
            if not os.path.exists(path):
                os.mkdir(path)
                break
            i += 1
    return path


class ParrotletSpider(scrapy.Spider):
    name = 'Parrotlet'
    # allowed_domains = ['twitter.com']
    # start_urls = ['http://twitter.com/']
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    api = tweepy.API(auth)
    
    #cria diretoria para dados e metadados caso nao exista        
    if not os.path.exists('meta'):
        os.mkdir('meta')
    if not os.path.exists('data'):
        os.mkdir('data')
        

    def start_requests(self):        
        self.spider_output_folder = create_dir(self.name, True)        
        
        terms = [
                    #hbo max
                    ('hbomax',        'hbomax'), 
                    # Disney
                    ('disneyplus',    'disney+'), 
                    ('disney+',       'disney+'), 
                    # Netflix
                    ('netflix' ,      'netflix'), 
                    # Star+
                    ('star+',         'star+'), 
                    # 'Globo Play'
                    ('globoplay',     'globoplay'), 
                    # 'prime video'
                    ('amazon prime',  'primevideo'), 
                    ('primevideo',    'primevideo'),
                    #Politica - So para ter volume e testar a aplicação
                    ('bolsonaro',    'Politica')
                ]
        terms = [('bolsonaro',    'Politica')]
        #terms = ['hbomax'] #, 'disneyplus', 'disney+', 'netflix', 'star+', 'globoplay', 'amazon prime', 'primevideo']
    
        for term in terms:           
            if(os.path.isfile(f'meta/{term[0]}.json')):
                with open(f"meta/{term[0]}.json",'r', encoding='utf-8') as meta_file:
                    meta = json.load(meta_file)
            else:
                meta = { 'search_term'          : term[0],                     
                        'search_term_group'    : term[1],
                        'newest_id'            : 1, 
                        'newest_date'          : datetime.datetime.fromtimestamp(0).strftime('%Y-%m-%d %H:%M:%S'), 
                        'oldest_id'            : 9999999999999999999,
                        'oldest_date'          : datetime.datetime.fromtimestamp(9999999999).strftime('%Y-%m-%d %H:%M:%S'), 
                        'cold_newest_id'       : 1, 
                        'cold_newest_date'     : datetime.datetime.fromtimestamp(0).strftime('%Y-%m-%d %H:%M:%S'), 
                        'total_returned_tweets': 0}           
            
            # Override no oldes_id para puxar elementos novos, na primeira busca
            meta['oldest_id'] = 9999999999999999999
            
            # print_warning(f"{json.dumps(meta, indent=4, sort_keys=True)}")
            url = f"Twitter://{term[0]}"
            yield scrapy.Request(url=url, meta=meta, callback=self.parseTweet)

    # Trata os Twitters            
    def parseTweet(self, response):        
        json_response  = json.loads(response.text)
        meta = { 'search_term'              : json_response['search_term'],
                 'search_term_group'        : json_response['search_term_group'],
                 'newest_id'                : json_response['newest_id'], 
                 'newest_date'              : json_response['newest_date'], 
                 'oldest_id'                : json_response['oldest_id'],
                 'oldest_date'              : json_response['oldest_date'],
                 'cold_newest_id'           : json_response['cold_newest_id'],
                 'cold_newest_date'         : json_response['cold_newest_date'],                 
                 'total_returned_tweets'    : json_response['total_returned_tweets'],
                 }  

        if(json_response['returned_tweets'] > 0):
            #Retornou tudo que podia, ir para proxima pagina
            if (json_response['returned_tweets'] == 100):
                print_info(f"Retornado {json_response['returned_tweets']} / {json_response['total_returned_tweets']} tweets de {bcolors.BOLD} {json_response['search_term']} {bcolors.ENDC} para o periodo de  {json_response['newest_date']} a {json_response['oldest_date']}")
                
                # meta['newest_id'] = 1  #  Força o ID mais novo sendo 1.
                yield scrapy.Request(url=response.url, meta=meta, callback=self.parseTweet, dont_filter = True)                
            # Terminou 
            else:
                print_sucess(f"Retornado {json_response['returned_tweets']} / {json_response['total_returned_tweets']} tweets de {bcolors.BOLD}  {json_response['search_term']} {bcolors.ENDC} para o periodo de  {json_response['newest_date']} a {json_response['oldest_date']}")                
        else:
            print_warning(f"Retornado {json_response['returned_tweets']} tweets de {bcolors.BOLD}  {json_response['search_term']} {bcolors.ENDC} sendo o mais antigo de {json_response['oldest_date']}")            

        with open(f"data/{meta['search_term']}.jl",'a', encoding='utf-8') as data_file:
            for tweet in json_response['data'] :
                line = json.dumps(tweet, sort_keys=True, ensure_ascii=False)
                data_file.write(f"{line}\n")    
                yield tweet

        #salva os metadados para consulta futura
        with open(f"meta/{meta['search_term']}.json",'w', encoding='utf-8') as meta_file:
            #atualiza o ultimo ID salvo
            meta['cold_newest_id']    = meta['newest_id']
            meta['cold_newest_date']  = meta['newest_date']
            json.dump(meta, meta_file, indent=4,sort_keys=True)        
