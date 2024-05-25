import json

from datetime import datetime
from db import get_existing_vehicles, insert_vehicles, get_existing_violations, insert_violations, insert_tickets

tickets = []
violations = {}
vehicles = {}

# read and prep the data we need
with open('violations.json') as f:
    for line in f:
        # parse the json on the line
        ticket = json.loads(line)
        # prepare our custom identifiers

        # since we don't have much info or more reliable unique identifier for vehicle, 
        # let's just assume that only 1 vehicle per combination of Make, Body, Color and Plate Expiry

        vehicle_code = "{}_{}_{}_{}".format(ticket['Make'], ticket['BodyStyle'], ticket['Color'], ticket['PlateExpiry'])

        # we do the same for vehicles
        if vehicle_code not in vehicles:
            vehicles[vehicle_code] = {
                'vehicle_make': ticket['Make'],
                'vehicle_body': ticket['BodyStyle'],
                'vehicle_color': ticket['Color'],
                'vehicle_plate_expiry': ticket['PlateExpiry'] if ticket['PlateExpiry'] else None,
                'vehicle_vin': ticket['VIN'] if ticket['VIN'] else None
            }

        # let's not rely on violation code alone
        # because some states may have the same code, but they are for different kind of violation
        violation_code = "{}_{}".format(ticket['ViolationCode'], ticket['RPState'])

        # check if we already have the violation prepared,
        # if not, add it in array
        if violation_code not in violations:
            violations[violation_code] = {
                'violation_code': ticket['ViolationCode'],
                'violation_description': ticket['ViolationDescr'],
                'violation_state': ticket['RPState'],
                'violation_fine': float(ticket['Fine']) if ticket['Fine'] else 0.00
            }
    
        # convert issue date and time to Y-m-d H:M:S format
        issue_date_obj = datetime.strptime(ticket["IssueData"], "%Y-%m-%dT%H:%M:%S")
        issue_date = issue_date_obj.strftime("%Y-%m-%d")

        # then, convert issue time to 24H format
        # ensure time is in the correct format by padding with leading zeros
        issue_time = ticket["IssueTime"].zfill(4)
        issue_time_obj = datetime.strptime(issue_time, "%H%M")
        issue_time = issue_time_obj.strftime("%H:%M")

        issue_datetime = "{} {}:00".format(issue_date, issue_time)
        
        # add the ticket
        tickets.append({
            'ticket_id': ticket['Ticket'],
            'ticket_route': ticket['Route'],
            'ticket_location': ticket['Location'],
            'ticket_coordinates': {
                'latitude': ticket['Latitude'],
                'longitude': ticket['Longitude'],
            },
            'ticket_issue_datetime': issue_datetime,
            'ticket_agency': ticket['Agency'],
            'ticket_meter_id': ticket['MeterId'],
            'ticket_marked_time': ticket['MarkedTime'].zfill(4),
            'vehicle_id': vehicle_code, # this is temporary, we'll change it later
            'violation_id': violation_code # this is temporary, we'll change it later
        })

# THIS IS UNDER THE ASSUMPTION THAT THIS IMPORT WILL BE REUSED 
# AND THAT THE DB IS EITHER EMPTY OR NOT

# now that we have all the data,
# check which items is needed for insert

# vehicles
# 1st, we query vehicles through the custom identification we did
vehicle_codes = list(vehicles.keys())
existing_vehicles = get_existing_vehicles(vehicle_codes)

# if there's a vehicle existing in db,
# loop through the results
if len(existing_vehicles):
    for vehicle_id, vehicle_code in existing_vehicles:
        # remove this vehicle in the list of vehicles for insertion
        del vehicles[vehicle_code]

# now that we have cleaned the vehicle list,
# let's insert in the database
if vehicles:
    insert_vehicles(list(vehicles.values()))

# then we do the same process on the violations
# query violations through the custom identification we did
violation_codenames = list(violations.keys())
existing_violations = get_existing_violations(violation_codenames)

# if there's a vehicle existing in db,
# loop through the results
if len(existing_violations):
    for violation_id, violation_code in existing_violations:
        # remove this violation in the list of violations for insertion
        del violations[violation_code]

# now that we have cleaned the violations list,
# let's insert in the database
if violations:
    insert_violations(list(violations.values()))

# now that we have the vehicles and violations all in db,
# we need to update tickets
# but first, let's prep the vehicles and violations for ease of access
existing_vehicles = get_existing_vehicles(vehicle_codes)
vehicles = {}
existing_violations = get_existing_violations(violation_codenames)
violations = {}
for i, exveh in enumerate(existing_vehicles):
    vehicles[exveh[1]] = exveh

for i, exvio in enumerate(existing_violations):
    violations[exvio[1]] = exvio

# we can then update tickets and append the vehicle_ids and violation_ids
for i, ticket in enumerate(tickets):
    # vehicle code
    tickets[i]['vehicle_id'] = vehicles[ticket['vehicle_id']][0]

    # violation code
    tickets[i]['violation_id'] = violations[ticket['violation_id']][0]
        
# since we've already appended the vehicle_ids and violation_ids
# the tickets are now ready to be inserted in the database
insert_tickets(tickets)