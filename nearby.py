# Google Places API has a maximum number of 60 results you get per search. This script
# traverses specific locations in grid manner and searches the radius.
import json
import requests
import xlsxwriter
import time, re

# Name of xlsx file to be generated
filename = "NgongRd,Kilimani,2"

def getNearbyJson():

    url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
    
    headers = {
            "Accept": "*/*",
    }
    
    # Location points in grid
    locations = [
        "-1.30578, 36.78499",
        "-1.29697, 36.78486",
        "-1.28839, 36.78482",
        "-1.27988, 36.78474",
        "-1.27151, 36.78466",
        "-1.26272, 36.78461",
        "-1.26262, 36.79177",
        "-1.27146, 36.79182",
        "-1.27976, 36.79182",
        "-1.2883, 36.79187",
        "-1.29684, 36.79191",
        "-1.30458, 36.79195",
        "-1.30467, 36.79898",
        "-1.29667, 36.79891",
        "-1.28822, 36.79878",
        "-1.27959, 36.79878",
        "-1.27157, 36.79865",
        "-1.26417, 36.79864",
        "-1.27386, 36.8043",
        "-1.2797, 36.80453",
        "-1.28798, 36.80482",
        "-1.29635, 36.80521",
        "-1.30454, 36.8056",
        "-1.30316, 36.81212",
        "-1.29595, 36.81139",
        "-1.2878, 36.81062",
        "-1.27922, 36.80984",
        "-1.29377, 36.81589",
        "-1.30076, 36.81813",
    ]

    # Initialize restaurants list to save all of them
    restaurants = []

    for location in locations:

        # Google API key plus keyword to search
        querystring = {
            "location":"{}".format(location), 
            "key": "AIzaSyA0GSXzv2wPLzrZUgcmFMf56k8jVtMApvI", 
            "keyword": "restaurant", 
            "radius": "500"
        }
    
        # Sleep for a few seconds to avoid blocking
        time.sleep(4)

        response = requests.request("GET", url, headers=headers, params=querystring)
        json_data = response.content
        response1 = json.loads(json_data)
        restaurants1 = response1['results']

        for resta1 in restaurants1:
            restaurants.append(resta1)
        
        # Check for page 2
        nextpage = response1.get('next_page_token')

        if nextpage:
            querystring = {"key":"AIzaSyA0GSXzv2wPLzrZUgcmFMf56k8jVtMApvI" ,"pagetoken": "{}".format(response1['next_page_token'])}

            time.sleep(3)

            response = requests.request("GET", url, headers=headers, params=querystring)
            json_data = response.content
            response2 = json.loads(json_data)
            restaurants2 = response2['results']

            for resta2 in restaurants2:
                restaurants.append(resta2)

            # Check for page 3 (last page)
            nextpage2 = response2.get('next_page_token')

            if nextpage2:
                querystring = {"key":"AIzaSyA0GSXzv2wPLzrZUgcmFMf56k8jVtMApvI" ,"pagetoken": "{}".format(response2['next_page_token'])}

                time.sleep(3)

                response = requests.request("GET", url, headers=headers, params=querystring)
                json_data = response.content
                response3 = json.loads(json_data)
                restaurants3 = response3['results']
                
                for resta3 in restaurants3:
                    restaurants.append(resta3)

            else:
                pass
  
    save_Nearby_Search(restaurants)

# Initiate Place IDs - used for searching more info about the place
placeids = set()

def save_Nearby_Search(allresta):

    workbook = xlsxwriter.Workbook('restas-{}.xlsx'.format(filename))
    worksheet = workbook.add_worksheet("firstSheet")

    worksheet.write(0, 0, "name")
    worksheet.write(0, 1, "location")
    worksheet.write(0, 2, "place_id")
    worksheet.write(0, 3, "rating")
    worksheet.write(0, 4, "types")
    worksheet.write(0, 5, "vicinity")
    
    for index, resta in enumerate(allresta):
        
        name = resta['name']
        location = str(resta['geometry']['location']['lat']) + ',' + str(resta['geometry']['location']['lng'])
        place_id = resta['place_id']
        placeids.add(place_id)
        rating = resta['rating']
        types = resta['types'][0]
        vicinity = resta['vicinity']

        worksheet.write(index+1, 0, name)
        worksheet.write(index+1, 1, location)
        worksheet.write(index+1, 2, place_id)
        worksheet.write(index+1, 3, rating)
        worksheet.write(index+1, 4, types)
        worksheet.write(index+1, 5, vicinity)

    workbook.close()        

    return "Saved data to xlsx file"


def getDetailsJson(placeids):

    url = "https://maps.googleapis.com/maps/api/place/details/json"
    
    headers = {
            "Accept": "*/*",
    }

    restadetails = []

    for placeid in placeids:

        querystring = {"key":"AIzaSyA0GSXzv2wPLzrZUgcmFMf56k8jVtMApvI" ,"place_id": "{}".format(placeid)}

        time.sleep(3.5)
        response = requests.request("GET", url, headers=headers, params=querystring)

        json_data = response.content
        response = json.loads(json_data)
        details = response["result"]

        restadetails.append(details)

    search_save_Details(restadetails)

def search_save_Details(restadetails):

    workbook = xlsxwriter.Workbook('restadetails-{}.xlsx'.format(filename))
    worksheet = workbook.add_worksheet("firstSheet")

    worksheet.write(0, 0, "name")
    worksheet.write(0, 1, "sublocality")
    worksheet.write(0, 2, "locality")
    worksheet.write(0, 3, "website")
    worksheet.write(0, 4, "phone")
    worksheet.write(0, 5, "address")
    worksheet.write(0, 6, "placeid")
    
    for index, detail in enumerate(restadetails):
        
        name = detail['name']
        sublocality = ""
        for address in detail['address_components']:
            if re.search(r'sublocality', address['types'][0]):
                sublocality = address['long_name']
        locality = ""
        for address in detail['address_components']:
            if address['types'][0] == "locality":
                locality = address['long_name']
            
        # sublocality = detail['address_components'][1]['long_name']
        # locality = detail['address_components'][2]['long_name']
        address = detail['formatted_address']
        placeid = detail['place_id']
        try:
            phone = detail['formatted_phone_number']
        except:
            phone = ""
        try:
            website = detail['website']
        except:
            website = ""

        worksheet.write(index+1, 0, name)
        worksheet.write(index+1, 1, sublocality)
        worksheet.write(index+1, 2, locality)
        worksheet.write(index+1, 3, website)
        worksheet.write(index+1, 4, phone)
        worksheet.write(index+1, 5, address)
        worksheet.write(index+1, 6, placeid)

    workbook.close()        

    return "Saved Details"


getNearbyJson()
time.sleep(4)
f = open("placeids-{}.txt".format(filename), "a")
f.write(str(placeids))
f.close()

getDetailsJson(placeids)