from django.db import models
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model

from random import randint
import re
import requests

#Constants
USERMODEL = get_user_model()
# Approver services that function with the program
    # append the target word , ?key=, and an owned key matching the useage to make functional
    #https://www.dictionaryapi.com/api/v3/references/thesaurus/json/{newWord}?key={freekey}
APPROVED_SERVICES_API_ROOTS = {"websterdictionary": "https://dictionaryapi.com/api/v3/references/collegiate/json/", "websterthesaurus": "https://dictionaryapi.com/api/v3/references/thesaurus/json/"}
#TESTING- Approved api keys are to be stored in relevent views only
DICTIONARY_SIZES = {'core':500, 'related':1500}
SEPERATOR_VALUE = {'csv':','}



# Create your models here.
class PasswordGeneration(models.Model):
   #Owner - Account related to Password recommendation, this uses auth modules GetUser() for modularity
    owner = models.ForeignKey(USERMODEL, verbose_name=("Connected_Owner"), on_delete=models.CASCADE)
   #Dictionary = Contains a list of words that can act as a core for password generation 
        ## For testing purposes the amount of words that can be stored will be set to 20.
    dictionaryCore = models.CharField(max_length=DICTIONARY_SIZES['core'], blank = True, null = True, default='')
    dictionaryRelated = models.CharField(max_length=DICTIONARY_SIZES['related'], blank = True, null = True, default='')
   #Requirements = User Defined Requirements, Contains a collection of bits of fixed length that act as flags
    #which detail which predefined requirements are desired for usage
        #TODO
    #USer defined minimum words used to derive new password - cannot be shorter than 3
    minimum_words = models.IntegerField(default=3)
    minimum_numbers = models.IntegerField(default=3)
    minimum_special_characters = models.IntegerField(default=3)


    class Meta:
        verbose_name = ("passwordgenerators")
        verbose_name_plural = ("passwordgenerators")
         
    def __str__(self):
        return self.owner.username

    #def get_absolute_url(self):
        #return reverse("_detail", kwargs={"pk": self.pk})
    
    #update minimum words: cannot be less than 3
    def update_minimum_word(self, value:int):
        if value > 2 and value != self.minimum_words:
            self.minimum_words = value
        return
    #determine if dictionary stored holds a csv list with no white spaces
    def confirm_valid_dictionary_core(self):
        # scan through dictionary
            #if a token is equivalent to a white space return false
        for token in self.dictionaryCore:
            if token == " ":
                return False
              
        #Return true if no white spaces exist
        return True
    #@ this function is to be expanded to function with mutiple differing apis, as some return json objects in differing orders and content lables
    def get_API_request_json(self, API_Service:str, word:str, key:str):
        """ fetches api request when provided a string that denotes the api service - provided in the class as a key-value, the word to search, and a access key \n
        Returns a json object if call response is valid ie 200 and if the response json has the key 'meta' , otherwise return None"""
        try:
            API_Service = API_Service.lower()
            if APPROVED_SERVICES_API_ROOTS[API_Service]:
                #create a api request  using the root of the request and adding the neccessary portions based on the api
                api_call_url = APPROVED_SERVICES_API_ROOTS[API_Service] +  word + '?key=' + key
                api_response = requests.get(api_call_url)
                print(f'url : {api_call_url}')
                print(f'API response = {api_response.status_code}')
                # if call returns a response
                if api_response.status_code == 200:
                    #if response exist return json object
                    if 'meta' in api_response.json()[0]: 
                        return api_response.json()
                    
                #raise exception  if the above arent valid
                else:
                    raise Exception

        except Exception:
           #if an error occures return None
           print('An error has occured while retrieving the response')
           return None
    #@ This function is to be expanded to swap functionality upon thesaurus or dictionary usage
    #Updates dictionary and the words related to the dictionary, assuming the core word can be added
    def update_dictionaries(self, new_word:str, API_Key_Dictionary:str, API_Key_Thesaurus:str, API_Service:str ='websterdictionary', API_Service_Helper = 'websterthesaurus' , b_remove = False):
        """Update user password generator model dictionary values- only functions with single words"""
        bword_can_be_added = self.bCan_add_word(new_word)
        api_dictionary_json = None
        if b_remove == False and bword_can_be_added:
            print('Attempting to add word')
            try:
                #determine if word exists
                api_dictionary_json:list|None = self.get_API_request_json(API_Service, new_word, API_Key_Dictionary)
                if api_dictionary_json == None:
                    print('Response return invalid - word not found in dictionary')
                    raise Exception
                    
            except Exception:
                print("An Error has occured during the proccess of getting the API request")
                return False
        
            # if word exists aka statues code returned and meta in response , add to core words (this function assumes a validity check has been completed)
            try:

                    core_words = self.list_core_words()
                    core_words.append(new_word) 
                    #Add related words to related dictionary
                    try: 
                        # get api response for words related to the new word
                        api_thesuraus_json:list|None = self.get_API_request_json(API_Service_Helper, new_word, API_Key_Thesaurus)  
                        
                        if api_thesuraus_json:  
                             
                            
                            # Create a list of antonomys words                  
                            try:
                                collection_of_antonyms = []
                                response_antonyms = api_thesuraus_json[0]['meta']['ants']
                                # reevaluate to inner list if provided response is a double layers list
                                if type(response_antonyms[0]) == list :
                                    response_antonyms = response_antonyms[0]
                                #if list containing antynoyms of word exists; add words to related words
                                if len(response_antonyms) > 0:
                                    for word in response_antonyms:
                                        #if word in antynyms not blank add to possible words 
                                        if  word != '': collection_of_antonyms.append(word + ',')
                                    
                            except print("An Error has occured while deriving list of antonyms from json response"):
                                raise Exception
                            # Create a collection of synonmous words 
                            try:
                                collection_of_synonyms = []
                                response_synonyms = api_thesuraus_json[0]['meta']['syns']
                                # reevaluate to inner list if provided response is a double layers list
                                if type(response_synonyms[0]) == list :
                                    response_synonyms = response_synonyms[0]
                                #if list containing antynoyms of word exists; add words to related words
                                if len(response_synonyms) > 0:
                                    for word in response_synonyms:
                                        #if word in antynyms not blank add to possible words 
                                        if  word != '': collection_of_synonyms.append(word + ',')
                                            
                                #print(f'Antonyms and synonyms derived from thesuarus are {API_response_related_words}\n ')
                            except print("An Error has occured while deriving list of synonyms from json response, this segment is skipped"):
                                raise Exception
                            
                        else:
                            print('No json response for thesuarus of provided word found')
                            
                    except Exception:
                        print('An error has occured while defining thesuarus values')
                        return
            except Exception:
                print("An error has occured while fetching data")
                return False
            #$ Determine related words that can be added to related words list - This variant ignores entries with blank spaces
            try:
                # determine list of words that dont exists in core or related that exists in list of synonyms and antynyms
                API_response_related_words = collection_of_antonyms + collection_of_synonyms
                free_random_words = []
                related_words = self.list_related_words()
                
                print(f'code : \n {API_response_related_words} \n {related_words}')
                
                for word_index in range(len(API_response_related_words)):
                    #if word exists in either set of used words or is blank skip it
                    if API_response_related_words[word_index] == '' or API_response_related_words[word_index] in core_words or API_response_related_words[word_index] in related_words:
                        continue
                    free_random_words.append(API_response_related_words[word_index])

                # Remove words with blank spaces present
                free_random_words_no_spaces = []
                for word in free_random_words:
                    if " " in word:
                        continue
                    free_random_words_no_spaces.append(word)

                #remove trailing ','(comma) from word
                for word_index in range(len(free_random_words_no_spaces)):
                    free_random_words_no_spaces[word_index] = free_random_words_no_spaces[word_index].replace(',','')
                
                free_random_words = free_random_words_no_spaces
                # if the list of words that can be added is greater then 0
                chosen_words = []
                if len(free_random_words) > 0:
                    print('entering loop for selecting random words')
                    #select  up to 3 random words from the list, take them from the list and add them to desired related words to append
                    for i in range(3):
                        if len(free_random_words) <= 0:
                            print('length reduced to 0, breaking out of loop')
                            break
                        print(f'Length of random selection {len(free_random_words)}')
                        random_selection = randint(0, len(free_random_words)-1)
                        chosen_words.append(free_random_words.pop(random_selection))
                        print(f'current chosen words : {chosen_words} index is {i}')
                        print(f'current free random words :{free_random_words}')
                        
                        
                    #append selected words to related words in csv - in this case the dictionary ends with a , already and the api results also end with ,
                    for word in chosen_words:
                        if word == '' or word in related_words:
                            continue
                        related_words.append(word)
                        self.dictionaryRelated += word + ','
                    
                    
                    #if core words is empty assign new was as initial core word, otherwise append new core word to core words
                    if self.dictionaryCore == '':
                        self.dictionaryCore = core_words[0]
                    else:         
                        #convert new corewords list into csv | and store in dictionary core                 
                        self.dictionaryCore = self.convert_to_csv(core_words)
                    self.save()
                    return True

                else:
                    print('No words could be added to related words: found to all exists already')
                    
            except Exception:
                print('An error has occured while correcting the users dictionaries')
                return False
            else:
                print('Custom Word support is currently not functional')
            return True
        # Otherwise, if the goal is to remove a word from core 
        else:
            
            # get all synonyms and antonyms of word
            api_thesuraus_json:list|None = self.get_API_request_json(API_Service_Helper,new_word,API_Key_Thesaurus)
            if api_thesuraus_json is not None:  
                
                try:
                     # create list of found antonyms                    
                    collection_of_antonyms = []
                    response_antonyms = api_thesuraus_json[0]['meta']['ants']
                    # reevaluate to inner list if provided response is a double layers list
                    if type(response_antonyms[0]) == list :
                        response_antonyms = response_antonyms[0]
                    #if list containing antynoyms of word exists; add words to related words
                    if len(response_antonyms) > 0:
                        for word in response_antonyms:
                            #if word in antynyms not blank add to possible words 
                            if  word != '': collection_of_antonyms.append(word + ',')
                            
                except Exception:
                    print("An Error has occured while deriving list of antonyms from json response, this segment is skipped")
                    return False
       
                try:
                    # create list of found synonyms    
                    collection_of_synonyms = []
                    response_synonyms = api_thesuraus_json[0]['meta']['syns']
                    # if double layers list - reevaluate to inner list 
                    if type(response_synonyms[0]) == list :
                        response_synonyms = response_synonyms[0]
                    #if list containing antynoyms of word exists; add words to related words
                    if len(response_synonyms) > 0:
                        for word in response_synonyms:
                            #if word in antynyms not blank add to possible words 
                            if  word != '': collection_of_synonyms.append(word + ',')
                                            
                                
                except print("An Error has occured while deriving list of synonyms from json response, this segment is skipped"):
                    raise Exception
                
                # remove all synonyms and antonyms from users related words
                collection_of_related_words = collection_of_synonyms + collection_of_antonyms
                new_related_list = []
                print(collection_of_related_words)
                for used_word in self.list_related_words():
                    if used_word not in collection_of_related_words:
                        new_related_list.append(used_word)

                #convert result into csv form and set models related value to it
                self.dictionaryRelated = self.convert_to_csv(new_related_list)
                
                #remove target word from models core word csv and set model core to new list 
                new_core = []
                for word in self.list_core_words():
                    if new_word in word:
                        continue
                    new_core.append(word)
                if len(new_core) == 0:
                    self.dictionaryCore = ''
                self.dictionaryCore = self.convert_to_csv(new_core)
                #save result
                self.save()
        return True                                                
    #@ Confirm if word can be added to dictionary core- size check and existence check
    def bCan_add_word(self, newWord):
        """Returns true if word not found in dictionary core"""
        dictionary = self.dictionaryCore
        value_seperator = ','
        str_list = re.split(value_seperator, dictionary)
        # if dictionary has words less than limit and new word doesnt increase value past limit continue the operation
        if len(dictionary) < DICTIONARY_SIZES['core'] and (len(newWord) + len(dictionary)) <= DICTIONARY_SIZES['core']:
            #if word doesnt already exists in dictionary - csv form
            if newWord not in str_list:
            # return true - this indicates that the desired word can be added to the dictionary list
                return True
        # otherwise return false
        return False
    #@ Remove the target word from users dictionaries:list
    def remove_word(self, words:list|str, dictionary:list):
        """Removes a word or list of words from a list excluding trailing ',' : input is a list of strings with no trailing commas"""
        
        result:list = []
        # if input is a string instead of a list
        if type(words) == str:
            for word_dict in dictionary:
                if word_dict == '' or words == word_dict:
                    continue
            result.append(word_dict)
        else:
            for dict_words in dictionary:
                if dict_words == '' or dict_words in words:
                    continue
                result.append(dict_words)
        return result     
    #@ Select a set number of words from the users related dictionary
    def select_related_words(self, word_count):
        # define the list
        dictionary_list = re.split(',', self.dictionaryRelated)
        selected_words:list = []
        # select a random word from list
        for i in range(word_count):
            random_int = randint(0, len(dictionary_list))
            if dictionary_list[random_int] not in selected_words : 
                selected_words += dictionary_list[random_int]
        return selected_words
    def convert_to_csv(self,list_of_words):
        """Convert list into csv string, list taken in must not have values with trailing commas"""
        #convert new corewords list into csv
        new_csv:str = ''
        for word in list_of_words:
            new_csv += word + ','
        return new_csv   
    #@ Generate a new string based on a the related words - embeds non special characters within the string
    def generate_string(self, minimum_size=10, maxiumum_size=60, minimum_related_words=2):
        try:
            # require min to be atleast 2x less than max
            if (minimum_size * 3) >  maxiumum_size:
                raise('Max size must be atleast 3x larger then minumum size')
            #create a string that will be output by call
            string_result = ''
            #create a list of numbers to use
            numbers = []
            for i in range(self.minimum_numbers):
                numbers.append(randint(0,9))
            # create a list of special characters to use 
            special_characters_ascii = []
            for i in range(self.minimum_special_characters):
                special_characters_ascii.append(chr(randint(58,64))) 
        except Exception:
            print('Exception raised during checking phase of generate_string - generating special characters')
            
        try:
            # if the word count in related words is less than 10 - generate a non human memorable string: fully random 
            if len(self.list_related_words()) < 10:
                print(f'GenerateString-> randomstring being generated ')
                #generete random string of minimum length  
                for i in range(minimum_size):
                    #randomly select a value that designates the type of character to use
                    random_value = randint(0,2)
                    if random_value == 0:
                        #if random value is 0 select a random alphabetical character
                        #select capital or lowercase 
                        choice = randint(0,1)
                        if choice == 0:
                            random_char = chr(randint(65,90))
                        else:
                            random_char = chr(randint(97,122))
                    #if random value is 1 select a character between the first half of special characters
                    elif random_value == 1:
                        random_char = chr(randint(33,39))  
                    # otherwise select a random character from the second half of special characters
                    else:
                        random_char = chr(randint(59,64)) 
                        
                    # after selecting a random character add it to output string
                    string_result+= random_char
                return string_result
            else:
                # otherwise select the minimum amount of required words from related dictionary
                related_words_list = self.list_related_words()
                related_word_selection = []
                while len(related_word_selection) < minimum_related_words:
                    random_int = randint(0, len(related_words_list))
                    #Add word to list of related words selected if not already present
                    if related_words_list[random_int] not in related_word_selection:
                        related_word_selection.append(related_words_list[random_int])
                    
                #when selected words are generated, populate the string result  with random values inside the string including the selected words
                #* for this implementation it is assumed that a related word is the first substring in the string
                #randomly select a related word from the list of words previosly selected 
                random_char = related_word_selection[0,randint(len(related_word_selection))]  
            #remove selected word from list
            related_word_selection.remove(random_char) 
            string_result+= random_char 
                
            #while the string result is under the minimum size and there are words that need to be used
            while True:
                #randomly select a value that designates the type of character to use
                random_value = randint(0,10)
                if random_value >= 3:
                    #if random value is 0 select a random special character
                    random_char = special_characters_ascii[randint(0, len(special_characters_ascii))]
                #if random value is is from 3 to 6
                elif 3 > random_value <= 6:
                    random_char = numbers[randint(0,len(numbers))] 
                else:
                    #randomly select a related word from the list of words previosly selected 
                    random_char = related_word_selection[0,randint(len(related_word_selection))]  
                    #remove selected word from list
                    related_word_selection.remove(random_char)  
                # after selecting a random character add it to output string
                string_result+= random_char
                if len(string_result) > minimum_size and len(related_word_selection) ==0:
                    break
                if len(string_result) >= maxiumum_size:
                    break     
                
            return string_result
        # -- The above works on the premise of ASCII characters being used
        except Exception:
            print('Exception raised during generation phase of generate_string')
            return 
    def list_core_words(self):
        """Returns a list"""
        if self.dictionaryCore != '':
            csv_as_list = re.split(SEPERATOR_VALUE['csv'], self.dictionaryCore)
            return list(filter(None, csv_as_list))
        return []
    def list_related_words(self):
        if self.dictionaryRelated != '':
            csv_as_list = re.split(SEPERATOR_VALUE['csv'], self.dictionaryRelated)
            return list(filter(None, csv_as_list))
        return []
    def flush_dictionaries(self):
        self.dictionaryCore = ''
        self.dictionaryRelated = '' 
        self.save()
        return