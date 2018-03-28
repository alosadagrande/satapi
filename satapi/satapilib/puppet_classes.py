from connection import *
import logger as logger

class SatAPIPuppetClasses(SatAPIConnection):
    # Constructor
    def __init__(self, URL, User, Password, Debug=False):
        SatAPIConnection.__init__(self, URL, User, Password, Debug)

    # Get a class by its Id number
    def getPuppetClass(self, Id):
        Response=self.GET(self.SatAPILocation + 'puppetclasses/' + str(Id))
        return Response

    # Get a class by its name
    def getPuppetClassByName(self, Name):
        #Response=self.GET(self.SatAPILocation + 'puppetclasses/' + str(Name))
        criteria = "name = %s" % Name
        Response=self.searchPuppetClasses(criteria)
        return Response

    # Search classes by a search criteria
    def searchPuppetClasses(self, criteria, count=99):
        Response=self.GET(self.SatAPILocation + 'puppetclasses/',
                            {'search': criteria, 'count': count, 'per_page': count})
        return Response

    # Create override order for a given class parameter
    def setPuppetClassSmartParameterOverridesOrder(self, PuppetClass,
            Parameter, OverridesOrder):
        Response=self.PUT(self.SatAPILocation + 'puppetclasses/' +
                            PuppetClass + '/smart_class_parameters/' +
                            Parameter, OverridesOrder)
        return Response

    # Get overrides for a given class parameter
    def getPuppetClassSmartParameterOverrides(self, PuppetClass, Parameter):
        JSONData={
                'count': 999,
                'per_page': 999
            }
        Response=self.GET(self.SatAPILocation + 'puppetclasses/' +
                            PuppetClass + '/smart_class_parameters/' +
                            Parameter + '/override_values', JSONData)
        return Response

    # Get smart class parameters id for a given search criteria
    def searchPuppetClassSmartParameterID(self, criteria, PuppetClass):
        Response=self.GET(self.SatAPILocation + 'puppetclasses/' + PuppetClass +
                         '/smart_class_parameters?search=key=' + criteria)
        return Response

    # Set/update override values for a given class parameter. Two API calls are needed:
    # 1. Get the sc-parameter id that needs to be updated
    # 2. Set the new matcher/value for the sc-parameter
    def setPuppetClassSmartParameterOverrides(self, PuppetClass,
        Parameter, OverridesJSON):

        try:
            #Get the sc-parameter id that needs to be updated
            Response_ParamID=self.searchPuppetClassSmartParameterID(Parameter,PuppetClass)
            paramID=Response_ParamID['results'][0]['id']
            #Set the new value for the sc-parameter if the sc-parameter does not exist
            Response=self.POST(self.SatAPILocation + 'smart_class_parameters/' + str(paramID) +
                              '/override_values', OverridesJSON)
        except:
            #If the sc-parameter matcher is already set. Check if it needs to be updated
            logger.info('sc-parameter matcher was already defined in %s PuppetClass.' % PuppetClass)
            Response=self.getPuppetClassSmartParameterOverrides(PuppetClass,
                            Parameter)
            try:
                OverridesJSON=json.loads(OverridesJSON)
                #Load match and value for new sc-parameter
                NewOverrideMatch=str(OverridesJSON['override_value']['match'])
                NewOverrideValue=str(OverridesJSON['override_value']['value'])
                logger.info('Searching for the matcher and value of the sc-parameter if needs to be overwritten: %s (%s)' % (str(NewOverrideMatch),PuppetClass))

                #Loop for each of the sc-parameter elements of the existing puppet class 
                for total_results in range(len(Response['results'])):
                    if NewOverrideMatch == str(Response['results'][total_results]['match']):
                        #sc-parameter found: Checking if needs to be updated
                        if NewOverrideValue != str(Response['results'][total_results]['value']):
                            logger.info('++++ sc-parameter matcher found: Updating existing override matching %s with id %s (%s)' %
                                        (str(Response['results'][total_results]['match']),str(Response['results'][total_results]['id']),PuppetClass))
                            logger.debug('Previous matcher value is %s and new value is %s (%s)' % (str(Response['results'][total_results]['value']),NewOverrideValue,PuppetClass))
                            ResponsePUT=self.PUT(self.SatAPILocation + 'puppetclasses/' +
                                               PuppetClass + '/smart_class_parameters/' +
                                               Parameter + '/override_values/' + str(Response['results'][total_results]['id']),
                                               json.dumps(OverridesJSON))
                            logger.debug('Update\'s server response: ' + str(ResponsePUT))
                        else:
                            logger.info('==== sc-parameter already has same value. Not updating')
                            logger.debug('Previous matcher value is %s and new value is %s' % (str(Response['results'][total_results]['value']),NewOverrideValue))

            except requests.exceptions.HTTPError as e:
                 self.exception(e.message)
                 Response = 0
        return Response

    #Method for fetching smart_class_params with all atributes
    def getSmartClassParameter(self, sp_id):
        """
        Args:
            sp_id (int): smart class parameter id
        """

        try:
            Response = self.GET(self.SatAPILocation +
                                "smart_class_parameters/" +
                                str(sp_id))
        except Exception as err:
            raise err

        return Response
    
    # Get all smart class parameters
    def getSmartClassParameters(self, count=99):
        Response=self.GET(self.SatAPILocation + 'smart_class_parameters', {'count': count, 'per_page': count})
        return Response
    
    # Get overrides for a Smart Clss Prameters
    def getSmartClassParameterOverride(self, Parameter, count=99):
        Response=self.GET(self.SatAPILocation + 'smart_class_parameters/' + str(Parameter) + '/override_values', {'count': count, 'per_page': count})
        return Response
    
    # Delete overrides from a Smart Class Parameter
    def deleteSmartClassSmartParameterOverrides(self, Parameter, Override):
        Response=self.DELETE(self.SatAPILocation + 'smart_class_parameters/' + str(Parameter) + '/override_values/' + str(Override))
	return Response
