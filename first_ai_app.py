from openai import OpenAI, OpenAIError


client = OpenAI()

instructions = """
You are an infrastructure incident assistant.

Analyze the incident provided by the system administrator.

Return:
1. A short incident summary
2. The likely cause
3. Three troubleshooting commands or checks
4. A safe recommended next action

Do not claim the cause is confirmed unless the evidence proves it.
Do not claim that you executed any commands.
Keep the response concise and practical.
"""


incident = input(
    "Describe your Linux, Windows, cloud, or network incident:\n> "
).strip()


if not incident:
    raise SystemExit("No incident was provided. Program stopped.")


try:
    response = client.responses.create(
        model="gpt-6-astra",
        instructions=instructions,
        input=incident
    )

    print("\nAI INFRASTRUCTURE INCIDENT ANALYSIS")
    print("-" * 40)
    print(response.output_text)

except OpenAIError as error:
    print("OpenAI API request failed:", error)