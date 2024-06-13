def detail_view(request, art_name):
    base_url = "http://apis.data.go.kr/5710000/benlService/nltyArtList"
    image_api_url = "http://apis.data.go.kr/5710000/benlService/artImgList"

    # 작품 정보 가져오기
    params = {
        "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
        "pageNo": "1",
        "numOfRows": "1",
        "returnType": "json",
        "artNm": art_name
    }

    response = requests.get(base_url, params=params)
    art_details = {}

    if response.status_code == 200:
        data = response.json()
        items = data.get('response', {}).get('body', {}).get('items', [])
        if items:
            art_details = items[0]

    # 이미지 정보 가져오기
    image_params = {
        "serviceKey": "gKat/nvnmi8i9zoiX+JsGzCTsAV75gkvU71APhj8FbnH3yX4kiZMuseZunM0ZpcvKZaMD0XsmeBHW8dVj8HQxg==",
        "pageNo": "1",
        "numOfRows": "5",
        "returnType": "json",
        "artNm": art_name
    }

    image_response = requests.get(image_api_url, params=image_params)
    images = []

    if image_response.status_code == 200:
        image_data = image_response.json()
        items = image_data.get('response', {}).get('body', {}).get('items', [])
        if items:
            images = items

    # 상세 정보와 이미지를 렌더링
    return render(request, 'detail.html', {'art_details': art_details, 'images': images})
