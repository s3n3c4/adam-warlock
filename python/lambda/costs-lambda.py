import boto3
import json
from datetime import date
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def get_data():

    # Accessing Cost Explorer API
    client = boto3.client('ce')

    # StartDate = 1st date of current month, EndDate = Todays date
    start_date = str(date(year=date.today().year, month=date.today().month, day=1).strftime('%Y-%m-%d'))
    end_date = str(date.today())

    print(f'StartDate: {start_date} - EndDate: {end_date}\n')

    # The get_cost_and_usage operation is a part of the AWS Cost Explorer API, which allows you to programmatically retrieve cost and usage data for your AWS accounts.
    response = client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        Filter={
            "Not": {
                'Dimensions': {
                    'Key': 'RECORD_TYPE',
                    'Values': ['Credit', 'Refund']
                }
            }
        },
        GroupBy=[
            {
                'Type': 'DIMENSION',
                'Key': 'SERVICE'
            }
        ]
    )

    mydict = response
    resource_name = []
    resource_cost = []
    

    total_resources_active = len(mydict['ResultsByTime'][0]['Groups'])

    for i in range(total_resources_active):
        a = (mydict['ResultsByTime'][0]['Groups'][i].values())
        b = list(a)
        resource_name.append(b[0][0])
        resource_cost.append(float(b[1]['UnblendedCost']['Amount']))

    dict0 = {}

    for i in range(total_resources_active):
        dict0[resource_name[i]] = resource_cost[i]

    billed_resources = {k: round(v, 2) for k, v in dict0.items() if v}

    formatted_billed_resources = {k: f'U$ {v}' for k, v in billed_resources.items()}

    total_cost = sum(billed_resources.values())
    formatted_total_cost = f'U$ {round(total_cost, 2)}'
    resource_name = [name for name in resource_name if 'Tax' not in name]
    
    

    print(f'Current Billed Resources of this month:', json.dumps(formatted_billed_resources, indent=4, sort_keys=True))
    print(f'Active Resources:', json.dumps(resource_name, indent=4, sort_keys=True))
    print(f'Total: {formatted_total_cost}')
    return billed_resources, resource_name

def send_email(bill, resources, sender, recipient):
    
    TodayDate = str(date.today())
    subject = f"AWS Bill Report - {TodayDate}"
    formatted_total_cost = round(sum(v for v in bill.values()), 2)
    
    
    
    # Email body template
    email_body = """
    <h3>Current Billed Resources for this month:</h3>
    <table>
        <tr>
            <th>Resource</th>
            <th>Cost</th>
        </tr>
        {bill}
    </table>
    
    <h3>Total Cost: {formatted_total_cost} dollars</h3>
    
    <h3>Active Resources:</h3>
    <ul>
        {resources}
    </ul>
    """
    
    # Format the email body
    formatted_body = email_body.format(
        bill='\n'.join(f"<tr><td>{k}</td><td>{v}</td></tr>" for k, v in bill.items()),
        resources='\n'.join(f"<li>{r}</li>" for r in resources),
        formatted_total_cost=formatted_total_cost
    )
  

    # Create the email
    msg = MIMEMultipart()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = recipient
    msg.attach(MIMEText(formatted_body,"html"))

    # Send the email using Amazon SES
    ses = boto3.client("ses")
    ses.send_raw_email(RawMessage={"Data": msg.as_bytes()})


def lambda_handler(event, context):
    bill,resource=get_data()
    send_email(bill, resource, "allanwork5@yahoo.com.br","allanwork5@yahoo.com.br")
    return {
        'statusCode': 200,
        'body': json.dumps('Email sent successfully')
    }

