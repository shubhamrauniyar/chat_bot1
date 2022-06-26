from geopy.geocoders import Nominatim
def completeaddress(lati,long):
    locator = Nominatim(user_agent="myGeocoder")
    #coordinates = "17.50221,78.477929"
    coordinates=lati+","+long;
    location = locator.reverse(coordinates)
    return str(location);
