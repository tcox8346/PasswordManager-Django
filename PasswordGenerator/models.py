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
                #print(f'url : {api_call_url}')
                #print(f'API response = {api_response.status_code}')
                # if call returns a response
                if api_response.status_code == 200:
                    #if response exist return json object
                    if 'meta' in api_response.json()[0]: 
                        print()
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
        # if word can be added attempt to add word to core list
        if b_remove == False and bword_can_be_added:
            print('Attempting to add word')
            try:
                #determine if word exists
                api_dictionary_json:list = self.get_API_request_json(API_Service, new_word, API_Key_Dictionary)
                if api_dictionary_json == None:
                    print('Response return invalid - word not found in dictionary')
                    return True
            except Exception:
                print("An Error has occured during the proccess of getting the API request")
                return False
        
            # if word exists aka statues code returned and meta in response , add to core words (this function assumes a validity check has been completed)
            try:
                    # get current list of core words
                    core_words = self.list_core_words()
                    # add new word to list 
                    core_words.append(new_word)
                    # convert list to csv form and store in database
                    self.dictionaryCore = self.convert_to_csv(core_words)
                    

                    #Add related words to related dictionary
                    try: 
                        # get api response for words related to the new word
                        api_thesuraus_json:list = self.get_API_request_json(API_Service_Helper, new_word, API_Key_Thesaurus)  
                        
                        if api_thesuraus_json:  
                            # Attempt to add related antonymous words to related words list                 
                            try:
                                self.__related_add_antonyms(api_thesuraus_json)

                            except print("An Error has occured while deriving list of antonyms from json response"):
                                raise Exception
                            # Attempt to add related synonoymous words to related words list                 
                            try:
                                self.__related_add_synonyms(api_thesuraus_json)
                                pass
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
            
            # Determine related words that can be added to related words list - This variant ignores entries with blank spaces
            api_dictionary_json:list = self.get_API_request_json(API_Service_Helper, new_word, API_Key_Thesaurus)
            #self.__related_add_antonyms(api_dictionary_json)
            #self.__related_add_synonyms(api_dictionary_json)
        # Otherwise, if the goal is to remove a word from core 
        else:    
            pass
        # save changes to model instance
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
    # TO BE IMPLEMENTED ##############################################################
    #@ Remove the target word from users dictionaries:list
    def remove_core_word(self, words:list, dictionary:list):
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
    # remove related words attributed to core word from related words dictionary
    def remove_related_words(self, core_word, API_Service_Helper,API_Key_Thesaurus):
        api_thesuraus_json:list|None = self.get_API_request_json(API_Service_Helper, core_word, API_Key_Thesaurus) 
         
        # check if json response has sub key "ants" in "meta"
        if "ants" in api_thesuraus_json[0]["meta"].keys():
            response_ants = api_thesuraus_json[0]["meta"]['ants']
            # check if antnyms length is greater than 0
            if len(response_ants) > 0:
                # determine if result is a single layer list 
                try:
                    # if not make subject list the inner single layer list
                    if type(response_ants[0]) == list:
                        response_ants = response_ants[0]
                except Exception:
                    pass 
                # remove up to 3 instances of the related if they exists in the related dictionary
                removed_count = 0
                related_words = self.list_related_words()
                for i in range(len(response_ants)):
                    if response_ants[i] in related_words and removed_count < 3:
                        removed_count += 1
                        related_words.pop(response_ants[i])
     
        # check if json response has sub key "syns" in "meta"
        if "syns" in api_thesuraus_json[0]["meta"].keys():
            response_syns = api_thesuraus_json[0]["meta"]['syns']
            # check if antnyms length is greater than 0
            if len(response_syns) > 0:
                # determine if result is a single layer list 
                try:
                    # if not make subject list the inner single layer list
                    if type(response_syns[0]) == list:
                        response_syns= response_syns[0]
                except Exception:
                    pass 
                # remove up to 3 instances of the related if they exists in the related dictionary
                removed_count = 0
                related_words = self.list_related_words()
                for i in range(len(response_syns)):
                    if response_syns[i] in related_words and removed_count < 3:
                        removed_count += 1
                        related_words.pop(response_syns[i])
    ################################################################################## 
    #@ Select a set number of words from the users related dictionary
    def select_related_words(self, word_count):
        try:
            # define the list
            dictionary_list = re.split(',', self.dictionaryRelated)
            selected_words:list = []
            # select a random word from list
            for i in range(word_count):
                random_int = randint(0, len(dictionary_list))
                if dictionary_list[random_int] not in selected_words : 
                    selected_words += dictionary_list[random_int]
            return selected_words
        except Exception:
            print("An error has occured during the selection of related words")
    def convert_to_csv(self,list_of_words):
        """Convert list into csv string, list taken in must not have values with trailing commas"""
        #convert new corewords list into csv
        new_csv:str = ''
        for word in list_of_words:
            new_csv += word + ','
        return new_csv   
    #@ Generate a new string based on a the related words - embeds non special characters within the string
    def generate_string(self, minimum_size=10, maxiumum_size=60, minimum_related_words=2):
        # if the user password generator instance has 3 or more words 
        print(len(self.list_core_words()))
        if len(self.list_related_words()) >= 3:
            related_words = self.list_related_words()
            # select up to from 2 to 3 of the words from the list randomly
            words = []
            for i in range(randint(2,3)):
               choice = randint(0, len(related_words)-1)
               count = 0
               while related_words[choice] in words:
                    choice = randint(0, len(related_words)-1)
                    count += 1
                    if count > 5:
                        break
               words.append(related_words[choice]) 
            
            # alter each word in the sublist in some form
            results = []
            for word in words:
                choice = randint(0,3)
                # alter by adding a number to the end
                if choice == 0 :
                    result = word + str(randint(0,9))
                    results.append(result)
                    
                # alter by adding a special character to the end
                if choice == 1 :
                    result = word +chr(randint(33,45))   
                    results.append(result)             
                # alter by replacing a value with a number
                elif choice == 2 :
                    result = ""
                    replace_index = randint(0, len(word)-1)
                    
                    for i in range(len(word)):
                        if i == replace_index:
                            result += str(randint(0,9))
                        else:
                            result += word[i] 
                    results.append(result)               
                # alter by replacing a value with a special character
                else :
                    result = ""
                    replace_index = randint(0, len(word)-1)
                    
                    for i in range(len(word)):
                        if i == replace_index:
                            result += chr(randint(33,45))
                        else:
                            result += word[i]     
                    results.append(result)
                
            # combine words into a single string
            final_result = ""
            for word in results:
                for char in word:
                    final_result += char
            # remove all blank spaces from word
            final_result = final_result.replace(" ","")
            # post processing check - confirm password requirements are met
            
            # atleast 1 special character 
            spc_count = 0
            num_count = 0
            for i in range(33,46):
                if chr(i) in final_result:
                    spc_count += 1
            # atleast 1 numeral
            for i in range(0,10):
                if str(i) in final_result:
                    num_count += 1
            
            # if less then the required amount, insert the required amount randomly inside the result
            if spc_count < self.minimum_special_characters:
                post_processed_result = ""
                current_index = 0
                final_result_index = 0
                insert_spc = 3 - spc_count
                random_inserts = []
                for i in range(insert_spc):

                    random_index = randint(0, len(final_result))
                    #if the index is already in the array calculate a new one
                    while random_index in random_inserts:
                        random_index = randint(0, len(final_result)-1)

                    # add random index to list 
                    random_inserts.append(random_index)
                # extend final result by inserting random special characters in the randomily decided indexs
                while len(post_processed_result) < len(final_result) + insert_spc:
                    if current_index in random_inserts:
                        post_processed_result += chr(randint(33,45)) 
                        current_index += 1
                        continue
                    post_processed_result += final_result[final_result_index]
                    final_result_index += 1
                    current_index += 1
                final_result = post_processed_result    
            #repeat process defined above for numerals 
                                # if less then the required amount, insert the required amount randomly inside the result
            if num_count < self.minimum_numbers:
                post_processed_result = ""
                current_index = 0
                final_result_index = 0
                insert_num = 3 - num_count
                random_inserts = []
                for i in range(insert_num):
                    random_index = randint(0, len(final_result)-1)
                    #if the index is already in the array calculate a new one
                    while random_index in random_inserts:
                        random_index = randint(0, len(final_result)-1)
                    # add random index to list 
                    random_inserts.append(random_index)
                # extend final result by inserting random special characters in the randomily decided indexs
                while len(post_processed_result) < len(final_result) + insert_num:
                    if current_index in random_inserts:
                        post_processed_result += str(randint(0,9)) 
                        current_index += 1
                        continue
                    
                    post_processed_result += final_result[final_result_index]
                    
                    final_result_index += 1
                    current_index += 1
                final_result = post_processed_result    

        
            return final_result
        #####################
                
        else:
            try:
                print("random password generation")
                # require min to be atleast 2x less than max
                if (minimum_size * 3) >  maxiumum_size:
                    raise('Max size must be atleast 3x larger then minumum size')
                #create a string that will be output by call
                print("1")
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
                print("2")
                # if the word count in related words is less than 10 - generate a non human memorable string: fully random 
                if len(self.list_related_words()) < 10:
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
        """Returns a list, base form is csv"""
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
    def __generate_usable_ascii(self):
        #create a list of numbers to use
        numbers = []
        for i in range(self.minimum_numbers):
            numbers.append(randint(0,9))
        # create a list of special characters to use 
        special_characters_ascii = []
        for i in range(self.minimum_special_characters):
            special_characters_ascii.append(chr(randint(58,64))) 
        return {"numbers": numbers, "spc": special_characters_ascii}
    def __display_corewords(self):
        print(f"current core words: {self.list_core_words()} \n current related words: {self.list_related_words()}")
    def __related_add_antonyms(self, jsonresponse):
        # check if json response has sub key "ants" in "meta"
        if "ants" not in jsonresponse[0]["meta"].keys():
            return
        # create reference to location
        response_syns = jsonresponse[0]["meta"]["ants"]
        # get reference to current related dicitonary
        related_dict = self.list_related_words()

        #print(jsonresponse[0]["meta"].keys())

        # check if antonyms have values: assumed single list if not do nothing
        if len(jsonresponse[0]["meta"]["ants"]) == 0:
            return
        # check if the first index in the above is a list if so make subject the list 
        try:
            if type(response_syns[0]) == list:
                response_syns = response_syns[0]
            
        except print(0):
            pass
        
        # determine if response has values
        if len(response_syns) == 0:
            return
        # if value is less than 3 but more than 0 
        if len(response_syns) >= 3:
            #check if words can be added to dictionary related, is not present in core words, and if so add them
       
            for i in range(3):
                random_index = randint(0, len(response_syns)-1)
                if response_syns[random_index] not in related_dict and response_syns[random_index] not in self.list_core_words() :
                    related_dict.append(response_syns[random_index])
            #return related list as csv 
            self.dictionaryRelated = self.convert_to_csv(related_dict)
            print(self.dictionaryRelated)
        return 
    def __related_add_synonyms(self, jsonresponse):
        # check if json response has sub key "ants" in "meta"
        if "syns" not in jsonresponse[0]["meta"].keys():
            return
        # create reference to location
        response_syns = jsonresponse[0]["meta"]["syns"]
        # get reference to current related dicitonary
        related_dict = self.list_related_words()

        #print(jsonresponse[0]["meta"].keys())

        # check if antonyms have values: assumed single list if not do nothing
        if len(jsonresponse[0]["meta"]["syns"]) == 0:
            return
        # check if the first index in the above is a list if so make subject the list 
        try:
            if type(response_syns[0]) == list:
                response_syns = response_syns[0]
            
        except print(0):
            pass
        
        # determine if response has values
        if len(response_syns) == 0:
            return
        # if value is less than 3 but more than 0 
        if len(response_syns) >= 3:
            #check if words can be added to dictionary related, and if so add them
       
            for i in range(3):
                random_index = randint(0, len(response_syns)-1)
                if response_syns[random_index] not in related_dict and response_syns[random_index] not in self.list_core_words():
                    related_dict.append(response_syns[random_index])
            #return related list as csv 
            self.dictionaryRelated = self.convert_to_csv(related_dict)
            print(self.dictionaryRelated)
        return 
  