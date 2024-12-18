import openai
import os

openai.api_key = os.environ.get('OPENAI_API_KEY')

def generate_fitness_plan(user_data):
    prompt = (
        f"사용자의 현재 체중: {user_data['weight']}kg\n"
        f"목표 체중: {user_data['target_weight']}kg\n"
        f"가슴: {user_data['chest']}인치, 허리: {user_data['waist']}인치, 허벅지: {user_data['thigh']}인치\n"
        f"목표 기간: {user_data['period']}일\n\n"
        "다음 형식에 맞춰 피트니스 계획을 제공해주세요:\n"
        "- 근력 운동:\n"
        "  - 운동 1: [운동 이름]\n"
        "    - [세트 수], [반복 횟수]\n"
        "  - 운동 2: [운동 이름]\n"
        "    - [세트 수], [반복 횟수]\n"
        "\n"
        "- 유산소 운동:\n"
        "  - 운동 1: [운동 이름]\n"
        "    - 주 [횟수], [시간]\n"
        "\n"
        "[30일 동안 운동 계획을 실천했을 때 예상되는 결과를 간단히 설명해주세요.]"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        fitness_plan = response.choices[0].message["content"].strip().replace('\n', '')

        return fitness_plan
    except Exception as e:
        return f"AI 요청 중 오류가 발생했습니다: {e}"