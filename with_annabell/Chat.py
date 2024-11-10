import asyncio
from ChatController import ChatController

async def main():
    chat_controller = ChatController()
    # Create choice
    ai_model = None
    print("Choose the model you want to interact with:")
    print("1. GPT-3 & Annabell blended")
    print("2. Gemini & GPT-3 without Annabell")
    choice = input("Enter your choice: ")
    if choice == '1':
        ai_model = 'GPT'
        print("You are interacting with GPT-3 Annabell blended model \n")
    elif choice == '2':
        ai_model = 'GPTGemini'
        print("You are interacting with GPT & Gemini \n")
    else:
        print("Invalid choice. Exiting the program.")
        return
    
    # Main interaction loop
    while True:
        
        # Get user input
        user_input = input("You: ")

        # Break the loop whiith exit
        if user_input.lower() == 'exit':
            break

        # Process the user input
        if ai_model == 'GPT':
            response = await chat_controller.create_prompt(user_input)
            print("\nBlended response:", response, "\n" )
            
        elif ai_model == 'GPTGemini':
            # Gemini Response
            Gemini_response = await chat_controller.gemini_response(user_input)
            print("\nGemini:", Gemini_response)
            
            # GPT Response
            GPT_response = await chat_controller.create_prompt_without_annabell(user_input)
            print("GPT:", GPT_response, "\n")
           
if __name__ == "__main__":
    asyncio.run(main())