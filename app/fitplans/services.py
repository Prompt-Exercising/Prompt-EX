import os

import openai

openai.api_key = os.environ.get("OPENAI_API_KEY")


def generate_fitness_plan(user_data):
    prompt = (
        f"사용자의 현재 체중: {user_data['weight']}kg\n"
        f"목표 체중: {user_data['target_weight']}kg\n"
        f"가슴: {user_data['chest']}인치, 허리: {user_data['waist']}인치, 허벅지: {user_data['thigh']}인치\n"
        f"운동 기간: {user_data['period']}일\n\n"
        "사용자의 신체 데이터를 기반으로 특정 부위에 중점을 둔 피트니스 계획을 제공해주세요:\n"
        "- 근력 운동:\n"
        "  - 운동 1: [운동 이름]\n"
        "    - [세트 수], [반복 횟수]\n"
        "    - [소모 칼로리]\n"
        "  - 운동 2: [운동 이름]\n"
        "    - [세트 수], [반복 횟수]\n"
        "    - [소모 칼로리]\n"
        "\n"
        "- 유산소 운동:\n"
        "  - 운동 1: [운동 이름]\n"
        "    - 주 [횟수], [시간]\n"
        "    - [소모 칼로리]\n"
        "\n"
        "- 하루 식사량:\n"
        "   - 칼로리 : [목표 체중을 위한 일일 권장 칼로리]"
        "   - 탄단지 : [음식을 섭취할 때 권장 하는 탄수화물, 단백질, 지방]"
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300,
            temperature=0.7,
        )
        # fitness_plan = response.choices[0].message["content"].strip().replace('\n', '')
        fitness_plan = response.choices[0].message["content"]
        return fitness_plan
    except Exception as e:
        return f"AI 요청 중 오류가 발생했습니다: {e}"


user_data = {
    "weight": 75.5,
    "target_weight": 70.0,
    "chest": 37.0,
    "waist": 32.0,
    "thigh": 21.5,
    "period": 30,
}

print(generate_fitness_plan(user_data))
