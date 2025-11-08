from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from dotenv import load_dotenv
from doc_analysing_agent.agent import agent
from google.genai import types
import uuid
import asyncio

load_dotenv()

new_session_service = InMemorySessionService()

initial_state = {
        "user_preferences": """
    I want to get critical insights from text data that i will provide to you.
    """,
}

APP_NAME = "Doc Analyser"
USER_ID = "user_1"
SESSION_ID = str(uuid.uuid4())

session = asyncio.run(new_session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID,state=initial_state))
    
runner = Runner(agent=agent, app_name=APP_NAME, session_service=new_session_service)

def create_message(user_text: str) ->str:
    message = types.Content(
        role="user",
        parts=[types.Part(text=user_text)]
        )

    events = runner.run(session_id=SESSION_ID, user_id=USER_ID, new_message=message)
    print("created events")
    for event in events:
        if event.is_final_response():
            if event.content and event.content.parts:
                return event.content.parts[0].text
            else: return "------Error"
        else: return "-------error"

if __name__ == "__main__":
    text1 = '''
Donald Trump Wins 2024 U.S. Presidential Election in Historic ComebackOn November 5, 2024, the United States held its presidential election, resulting in a historic political comeback for former President Donald J. Trump. Running as the Republican nominee with Ohio Senator J.D. Vance as his running mate, Trump defeated Democratic candidate and current Vice President Kamala Harris, who was paired with Minnesota Governor Tim Walz.Trump secured a total of 312 electoral votes to Harris's 226, winning key battleground states including Pennsylvania, Michigan, and Georgia. Although the popular vote remained close—with Trump receiving 49.8% and Harris 48.3%—the electoral margin was decisive. This victory marks Trump's second, non-consecutive term in the White House, making him the first U.S. president to achieve such a comeback since Grover Cleveland in the late 19th century.The 2024 elections also saw a significant shift in congressional power. Republicans gained four seats in the U.S. Senate, flipping control from the Democrats and securing a majority. In the House of Representatives, the GOP maintained a narrow majority, giving the party full control of Congress alongside the presidency.A notable feature of this election was the shifting demographics in voter turnout and preference. Trump made substantial gains among Hispanic voters, receiving nearly 48% of their support, and also improved his standing with Black (15%) and Asian (40%) voters compared to previous elections. Young male voters under 50 leaned more Republican this cycle, contributing to Trump’s victories in several swing states. Turnout was also a crucial factor; Republican voter enthusiasm translated into higher turnout rates in critical districts.The election was conducted smoothly, with no major disruptions or legal challenges delaying certification. The results were certified by Congress on January 6, 2025, and Trump is scheduled to be inaugurated on January 21, 2025.International observers noted the peaceful transition of power and the continued resilience of U.S. democratic institutions, despite political polarization. The Biden administration, while disappointed by the results, issued a statement congratulating the incoming leadership and reaffirming the importance of unity and democratic continuity.The 2024 U.S. election has reshaped the American political landscape, reaffirming the deep divides within the electorate while highlighting the evolving demographics and priorities of voters. As Trump prepares to return to the Oval Office, the world watches closely to see how his administration will approach global affairs, domestic policy, and bipartisan governance in a deeply polarized nation.
'''
    while True:
        text = input("Enter document text: ")
        print(create_message(text))
        c = input("do you wnat to continue? (y/n): ")
        if c == 'n':
            break


    # print(create_message(text1))
