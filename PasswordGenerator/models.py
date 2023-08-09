from django.db import models
from django.urls import reverse
from django.http import JsonResponse
from django.contrib.auth import get_user_model
import requests
from random import randint
import re

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
        Returns a json object if call response is valid , otherwise return None"""
        try:
            API_Service = API_Service.lower()
            if APPROVED_SERVICES_API_ROOTS[API_Service]:
                #create a api request  using the root of the request and adding the neccessary portions based on the api
                api_call_url = APPROVED_SERVICES_API_ROOTS[API_Service] +  word + '?key=' + key
                api_response = requests.get(api_call_url)
                
                # if call returns a response
                if api_response.status_code == 200:
                    #if response exist return json object
                    return api_response.json()
            #return None if the above arent valid
            return None
        except Exception:
           #if an error occures return None
           return None
    #@ This function is to be expanded to swap functionality upon thesaurus or dictionary usage
    #Updates dictionary and the words related to the dictionary, assuming the core word can be added
    def update_dictionaries(self, new_word:str, API_Key_Dictionary:str, API_Key_Thesaurus:str, API_Service:str ='websterdictionary', API_Service_Helper = 'websterthesaurus' , b_remove = False):
        """Update user password generator model dictionary values- only functions with single words"""
        bword_can_be_added = self.bCan_add_word(new_word)
        if b_remove == False and bword_can_be_added:
            try:
                #determine if word exists
                api_dictionary_json:list|None = self.get_API_request_json(API_Service, new_word, API_Key_Dictionary)
            except Exception:
                print("An Error has ouccred during the proccess of getting the API request")
                return
        
        # if word exists aka statues code returned and meta in response , add to core words (this function assumes a validity check has been completed)
        if api_dictionary_json:
            core_words = self.list_core_words()
            core_words.append(new_word) 
            #Add related words to related dictionary
            try: 
                # get api response for words related to the new word
                api_thesuraus_json:list|None = self.get_API_request_json(API_Service_Helper, new_word, API_Key_Thesaurus)  
                
                if api_thesuraus_json:  
                    # create list of found related words                    
                    try:
                        collection_of_antonyms = []
                            #if list containing antynoyms of word exists; add words to related words
                        if len(api_thesuraus_json[0]['meta']['ants']) > 0:
                            
                            if type(api_thesuraus_json[0]['meta']['ants']) == list:
                                for word_index in range(len(api_thesuraus_json[0]['meta']['ants'][0])):
                                    #if word in antynyms not blank add to possible words 
                                    if api_thesuraus_json[0]['meta']['ants'][0][word_index] != '':
                                        collection_of_antonyms.append(api_thesuraus_json[0]['meta']['ants'][0][word_index] + ',')
                            else:
                                print(f"api_thesuraus_json[0]['meta']['ants'] is not of type list\n" )
                            
                            
                    except print("An Error has occured while deriving list of antonyms from json response, this segment is skipped"):
                        raise Exception
                        
                    try:
                        collection_of_synonyms = []
                            #if list containing synonyms of word exists add words to related words
                        if len(api_thesuraus_json[0]['meta']['syns'][0]) > 0:
                            if type(api_thesuraus_json[0]['meta']['syns']) == list:
                                for word_index in range(len(api_thesuraus_json[0]['meta']['syns'][0])):
                                    if api_thesuraus_json[0]['meta']['syns'][0][word_index] != '':
                                        collection_of_synonyms.append(api_thesuraus_json[0]['meta']['syns'][0][word_index] + ',') 
                                    
                        #print(f'Antonyms and synonyms derived from thesuarus are {API_response_related_words}\n ')
                    except print("An Error has occured while deriving list of synonyms from json response, this segment is skipped"):
                        raise Exception
                    
                else:
                    print('No json response for thesuarus of provided word found')
                    
            except Exception:
                print('An error has occured while defining thesuarus values')
                return
            
        #$ Determine related words that can be added to related words list - This variant ignores entries with blank spaces
        try:
            # determine list of words that dont exists in core or related that exists in list of synonyms and antynyms
            API_response_related_words = collection_of_antonyms + collection_of_synonyms
            free_random_words = []
            related_words = self.list_related_words()
            
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
            #remove trailing , from word
            for word_index in range(len(free_random_words_no_spaces)):
                free_random_words_no_spaces[word_index] = free_random_words_no_spaces[word_index].replace(',','')
            
            free_random_words = free_random_words_no_spaces
            # if the list of words that can be added is greater then 0
            chosen_words = []
            if len(free_random_words) > 0:
               
                #select  up to 3 random words from the list, take them from the list and add them to desired related words to append
                for i in range(3):
                    if len(free_random_words) == 0:
                        break
                    random_selection = randint(0, len(free_random_words))
                    chosen_words.append(free_random_words.pop(random_selection))
                
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
                    #convert new corewords list into csv
                    new_core_words_csv = ''
                    for word in core_words:
                        new_core_words_csv += word + ','
                    #assign new cord word csv to dictionare core
                    self.dictionaryCore = new_core_words_csv
                self.save()
                return

            else:
                print('No words could be added to related words: found to all exists already')
                
        except Exception:
            print('An error has occured while correcting the users dictionaries')
            return
        
        #if the purpose is to remove a word and its related words from the dictionary
        else:
            # start process only if word exists in users core words
            core_words = self.list_core_words()
            if new_word in core_words:
                try:
                    #determine if word exists in global dictionary
                    api_dictionary_json = self.get_API_request_json(API_Service, new_word, API_Key_Dictionary)
                    
                except Exception:
                    print("An Error has ocurred during the proccess of getting the API request")
                    return
                
                #if the word doesnt exist as a standard word in the english dicitonary - remove the word from core and return
                if api_dictionary_json == None:
                    self.b_remove_word(list[new_word])
                    return
                
                # if word exists in api dictionary , (this function assumes a validity check has been completed)
                related_words_query = self.get_API_request_json(API_Service,new_word,API_Key_Thesaurus)
                API_response_related_words = []
                
                
                
                for word in related_words_query[0]['meta']['ants']:
                    API_response_related_words += word
                for word in related_words_query[0]['meta']['syns']:
                    API_response_related_words += word
                #remove words from user dictionaries
                self.b_remove_word(new_word, 'core')
                self.b_remove_word(API_response_related_words)
        
        return 
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
    #@ Remove the target word from users dictionaries
    def b_remove_word(self,target_words:list, target_dictionary:str = 'related'):
        try:
            if target_dictionary=="related":
                dictionary = self.dictionaryRelated
            else:
                dictionary = self.dictionaryCore
        except Exception :
            print('Unable to assign dictionarys ')
            return False
        
        try:
            #determine if word exists in dictionary
            str_list = re.split(value_seperator, dictionary)
            for word in str_list:
                if word not in str_list:
                    print('Word does not currently exists in list, cannot be removed')
                    return 
        
                
            #@ Remove a word/list of words from the dictionary in csv form 
            #create output placeholder
            output_dictionary = ''
            # Create a list based on the provided csv string using regular expressions
            value_seperator = ','
            
            # populate a new string- output - with each element of the split list,, excluding the words targeted
            for word in str_list:
                if word in target_words or word == '':
                    continue
                output_dictionary + word + ',' # this value is the newest iteration of the dictionary
            if dictionary == self.dictionaryRelated and self.dictionaryCore != self.dictionaryRelated:
                self.dictionaryRelated = output_dictionary
            elif dictionary == self.dictionaryCore and self.dictionaryCore != self.dictionaryRelated:
                self.dictionaryCore = output_dictionary
        except Exception : 
            print('An error has occured while removing word')
            return False
    #@ Select a set number of words from related dictionary
    def select_related_words(self, word_count):
        dictionary_list = re.split(',', self.dictionaryRelated)
        selected_words = []
        for i in range(word_count):
            selected_words += dictionary_list[randint(0, len(dictionary_list))]
        return selected_words    
    #@ Generate a new string based on a the related words - embeds non special characters within the string
    def generate_string(self, minimum_size=20, maxiumum_size=60, minimum_related_words=2):
        try:
            # require min to be atleast 2x less than max
            if (minimum_size * 3) >  maxiumum_size:
                raise('Max size must be atleast 3x larger then minumum size')
            #create a string that will be output by call
            string_result = ''
            #create a list of numbers to use
            numbers = []
            for i in range(self.minimum_numbers):
                numbers += randint(0,9)
            # create a list of special characters to use 
            special_characters_ascii = []
            for i in range(self.minimum_special_characters):
                special_characters_ascii += randint(58,64)
        except:
            print('Exception raised during checking phase of generate_string')
            
        try:
            # if the word count in related words is less than 3 - generate a non human memorable string: fully random 
                ##Code to print current length being checked
                    #remove_obj = len(re.split(SEPERATOR_VALUE['csv'], self.dictionaryRelated))
                    #print(f'object length = {remove_obj}')
                ##
            if len(re.split(SEPERATOR_VALUE['csv'], self.dictionaryRelated)) < 3:
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
                related_words_list = re.split(SEPERATOR_VALUE['csv'], self.dictionaryRelated)
                related_word_selection = []
                while len(related_word_selection) < minimum_related_words:
                    selected_word = related_words_list[randint(0, len(related_words_list))]
                    #if selected word is already present in word selection - repeat until new word is found
                    if selected_word in related_word_selection:
                        continue
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
                #if random value is is between 3 and 6
                elif 3 > random_value <= 5:
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
        except :
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
    #Testing Functions
        #function that test removing word from core - excludes modifiying supplementary dictionaries, these functions do not use api calls
    def Testb_remove_word(self, old_word:str):
        try:
            dictionary = self.dictionaryCore
           
        except print('Unable to assign dictionarys '):
            return False
        
        try:
            #Try to calculate new dictionary results
                #@ Target Dictionary
            #@ Remove a word from the dictionary - search for related words and remove them from a related dictionary , core words to related words
            #create output placeholder
            output_dictionary = ''
            # Create a list based on the provided csv string using regular expressions
            value_seperator = ','
            str_list = re.split(value_seperator, dictionary)
            print(f'testbb_remove_word ->str_list: {str_list}')
            for value in str_list:
                if value == old_word or value=='':
                    continue
                output_dictionary += f'{value},'
                  
            self.dictionaryCore = output_dictionary
            self.save()
            print('result saved')
            
        except Exception :
            print('An error has occured while removing word')
            return False
       
        return True
    def Test_update_dictionary(self, new_word:str, API_Key_Dictionary:str, API_Key_Thesaurus:str, API_Service:str ='websterdictionary', API_Service_Helper = 'websterthesaurus',b_remove = False):
        """Test code to update models core dictionary csv using test methods. This version does not save the the model \n 
        Not to be used for production"""
        
        bword_can_be_added = self.bCan_add_word(new_word)
        if b_remove == False and bword_can_be_added:
            try:
                #determine if word exists
                api_dictionary_json:list|None = self.get_API_request_json(API_Service, new_word, API_Key_Dictionary)
            except Exception:
                print("An Error has ouccred during the proccess of getting the API request")
                return
        
        # if word exists aka statues code returned and meta in response , add to core words (this function assumes a validity check has been completed)
        if api_dictionary_json:
            core_words = self.list_core_words()
            print(f'Your initial core words are {core_words} \n csv form is {self.dictionaryCore}')
            core_words.append(new_word) 
            print(f'potential new core words are {core_words}')
            #Add related words to related dictionary
            try: 
                # get api response for words related to the new word
                api_thesuraus_json:list|None = self.get_API_request_json(API_Service_Helper, new_word, API_Key_Thesaurus)  
                
                if api_thesuraus_json:  
                    # create list of found related words                    
                    try:
                        collection_of_antonyms = []
                            #if list containing antynoyms of word exists; add words to related words
                        if len(api_thesuraus_json[0]['meta']['ants']) > 0:
                            
                            if type(api_thesuraus_json[0]['meta']['ants']) == list:
                                for word_index in range(len(api_thesuraus_json[0]['meta']['ants'][0])):
                                    #if word in antynyms not blank add to possible words 
                                    if api_thesuraus_json[0]['meta']['ants'][0][word_index] != '':
                                        collection_of_antonyms.append(api_thesuraus_json[0]['meta']['ants'][0][word_index] + ',')
                            else:
                                print(f"api_thesuraus_json[0]['meta']['ants'] is not of type list\n" )
                            
                            
                    except print("An Error has occured while deriving list of antonyms from json response, this segment is skipped"):
                        raise Exception
                        
                    try:
                        collection_of_synonyms = []
                            #if list containing synonyms of word exists add words to related words
                        if len(api_thesuraus_json[0]['meta']['syns'][0]) > 0:
                            if type(api_thesuraus_json[0]['meta']['syns']) == list:
                                for word_index in range(len(api_thesuraus_json[0]['meta']['syns'][0])):
                                    if api_thesuraus_json[0]['meta']['syns'][0][word_index] != '':
                                        collection_of_synonyms.append(api_thesuraus_json[0]['meta']['syns'][0][word_index] + ',') 
                                    
                        #print(f'Antonyms and synonyms derived from thesuarus are {API_response_related_words}\n ')
                    except print("An Error has occured while deriving list of synonyms from json response, this segment is skipped"):
                        raise Exception
                    
                else:
                    print('No json response for thesuarus of provided word found')
                    
            except Exception:
                print('An error has occured while defining thesuarus values')
                return
            
        #$ Determine related words that can be added to related words list - This variant ignores entries with blank spaces
        try:
            # determine list of words that dont exists in core or related that exists in list of synonyms and antynyms
            API_response_related_words = collection_of_antonyms + collection_of_synonyms
            free_random_words = []
            related_words = self.list_related_words()
            print(f"initial state: related_words{related_words}")
            
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
            #remove trailing , from word
            for word_index in range(len(free_random_words_no_spaces)):
                free_random_words_no_spaces[word_index] = free_random_words_no_spaces[word_index].replace(',','')
            
            free_random_words = free_random_words_no_spaces
            # if the list of words that can be added is greater then 0
            chosen_words = []
            if len(free_random_words) > 0:
                print(f'List derived for selection is {free_random_words}')
                print(f'Selecting 3 random words - random_word list length: {len(free_random_words)}')
                #select  up to 3 random words from the list, take them from the list and add them to desired related words to append
                
                print(f'selecting 3 words from {free_random_words}')
                for i in range(3):
                    if len(free_random_words) == 0:
                        break
                    random_selection = randint(0, len(free_random_words))
                    chosen_words.append(free_random_words.pop(random_selection))
                
                #append selected words to related words in csv - in this case the dictionary ends with a , already and the api results also end with ,
                print(f'Selected words are: {chosen_words}')
                for word in chosen_words:
                    if word == '' or word in related_words:
                        continue
                    related_words.append(word)
                    self.dictionaryRelated += word + ','
                print(f'final related_words object :{related_words}')
                
                
                #if core words is empty assign new was as initial core word, otherwise append new core word to core words
                if self.dictionaryCore == '':
                    self.dictionaryCore = core_words[0]
                else:         
                    #convert new corewords list into csv
                    new_core_words_csv = ''
                    for word in core_words:
                        new_core_words_csv += word + ','
                    #assign new cord word csv to dictionare core
                    self.dictionaryCore = new_core_words_csv
                print(f"New core word csv is {self.dictionaryCore}")  
                self.save()
                return

            else:
                print('No words could be added to related words: found to all exists already')
                
        except Exception:
            print('An error has occured while correcting the users dictionaries')
            return
        
        #if the purpose is to remove a word and its related words from the dictionary
        else:
            # start process only if word exists in users core words
            core_words = self.list_core_words()
            if new_word in core_words:
                try:
                    #determine if word exists in global dictionary
                    api_dictionary_json = self.get_API_request_json(API_Service, new_word, API_Key_Dictionary)
                    
                except Exception:
                    print("An Error has ocurred during the proccess of getting the API request")
                    return
                
                #if the word doesnt exist as a standard word in the english dicitonary - remove the word from core and return
                if api_dictionary_json == None:
                    self.b_remove_word(list[new_word])
                    return
                
                # if word exists in api dictionary , (this function assumes a validity check has been completed)
                related_words_query = self.get_API_request_json(API_Service,new_word,API_Key_Thesaurus)
                API_response_related_words = []
                
                
                
                for word in related_words_query[0]['meta']['ants']:
                    API_response_related_words += word
                for word in related_words_query[0]['meta']['syns']:
                    API_response_related_words += word
                #remove words from user dictionaries
                self.b_remove_word(new_word, 'core')
                self.b_remove_word(API_response_related_words)
        
        return 
    def Test_API_Call(self,API_Service:str, word:str, key:str ): 
        """Method to test if api call responds with a valid response"""
        API_Service = API_Service.lower()
        if APPROVED_SERVICES_API_ROOTS[API_Service]:
            #create a api request  using the root of the request and adding the neccessary portions based on the api
            api_call_url = APPROVED_SERVICES_API_ROOTS[API_Service] + word + '?key=' + key
            api_response = requests.get(api_call_url)
            if api_response.status_code == 200:
                print(f'Api call to url {api_call_url} successful') 
                if  'meta' in api_response.json()[0]:
                    # return the json response 
                    print('meta keyword in response')
                   
                return api_response     
        return
    def Test_select_random_word(self, API_response_json):
        """ Test code to update models core dictionary csv using test methods. This version uses the response of an api call \n 
        Not to be used for production"""
        try:
                # determine list of words that dont exists in core or related that exists in list of synonyms and antynyms
                selected_words = []
                free_random_words = []
                core_words = self.list_core_words()
                related_words = self.list_related_words()
                print(f'known core words: {core_words} \nKnown related words: {related_words} \n')
                print(f'API_response_related_words: {API_response_json} \n')
                
                for word_index in range(len(API_response_json)):
                    #if word exists in either set of used words or is blank skip it
                    if API_response_json[word_index] == '' or API_response_json[word_index] in core_words or API_response_json[word_index] in related_words:
                        continue
                    free_random_words += API_response_json[word_index]
                print(f'Free random wordss: {free_random_words} \n')   
                # if the list of words that can be added is greater then 0
                if len(free_random_words) > 0:
                    #select  up to 3 random words from the list, take them from the list and add them to desired related words to append
                    for i in range(3):
                        selected_words += free_random_words.pop(randint(0, len(free_random_words)))
                        
                    # append selected words to related words in csv - in this case the dictionary ends with a , already
                    for word in selected_words:
                        self.dictionaryRelated + 'word' + ','
                else:
                    print('No words could be added to related words: found to all exists already')
                    return
                    
        except Exception:
            print('An error has occured while correcting the users dictionaries')
            return