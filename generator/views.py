from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from openai import OpenAI
import os

openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class GenerateImageView(APIView):
    def post(self, request):
        user_prompt = request.data.get('prompt')
        if not user_prompt:
            return Response({'error': 'Missing prompt'}, status=status.HTTP_400_BAD_REQUEST)

        # Step 1: Enrich the prompt (placeholder)
        # In future, fetch data from Reddit, Twitter, etc.
        enriched_prompt = f"High-quality digital art of {user_prompt}, in the style of Brawl Stars, vibrant and colorful."

        # Step 2: Use GPT to make it more descriptive
        try:
            gpt_response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert Brawl Stars skin designer."},
                    {"role": "user", "content": f"Create a vivid description for: {enriched_prompt}"}
                ]
            )
            detailed_prompt = gpt_response.choices[0].message.content.strip()
        except Exception as e:
            return Response({'error': f'GPT error: {str(e)}'}, status=500)

        # Step 3: Use DALL·E or similar image generation
        try:
            image_response = openai_client.images.generate(
                model="dall-e-3",
                prompt=detailed_prompt,
                n=1,
                size="1024x1024"
            )
            image_url = image_response.data[0].url
        except Exception as e:
            return Response({'error': f'Image generation error: {str(e)}'}, status=500)

        return Response({
            "user_prompt": user_prompt,
            "enriched_prompt": detailed_prompt,
            "image_url": image_url
        }, status=status.HTTP_200_OK)
