
// 회원가입 유효성 검사 코드들이지만 장고에서 알아서 해주는 관계로 주석처리
//document.addEventListener("DOMContentLoaded", function() {
//    // 폼 요소 선택
//    const form = document.querySelector('#signup_form');
//
//    // 이벤트 리스너 등록
//    form.addEventListener('submit', function(event) {
//        // 기본 이벤트 중단 (폼 제출 방지)
//        event.preventDefault();
//
//        const usernameInput = document.getElementById('username');
//        const passwordInput = document.getElementById('password');
//        const password_check = document.getElementById('password_check');
//        const addressInput = document.getElementById('address');
//
//        // 아이디 유효성 검사 (최소 5글자 이상)
//        if (usernameInput.value.length < 5) {
//            alert("아이디는 최소 5글자 이상이어야 합니다.");
//            return;
//        }
//
//        // 비밀번호 유효성 검사 (예시: 최소 8글자 이상)
//        if (passwordInput.value.length < 8) {
//            alert("비밀번호는 최소 8글자 이상이어야 합니다.");
//            return;
//        }
//
//        // 비밀번호 확인
//        if (passwordInput.value !== password_check.value) {
//            alert("비밀번호가 일치하지 않습니다.");
//            return;
//        }
//
//        // 주소 유효성 검사 (예시: 빈 값 체크)
//        if (addressInput.value.trim() === "") {
//            alert("주소를 입력하세요.");
//            return;
//        }
//
//        // 모든 조건이 충족되면 폼 제출
//        form.submit();
//    });
//});

// 슬릭 슬라이더
$(function(){
    $('.slick_container').slick({
        slide: 'div',        //슬라이드 되어야 할 태그 ex) div, li
        infinite : true,     //무한 반복 옵션
        slidesToShow : 1,        // 한 화면에 보여질 컨텐츠 개수
        slidesToScroll : 1,        //스크롤 한번에 움직일 컨텐츠 개수
        speed : 100,     // 다음 버튼 누르고 다음 화면 뜨는데까지 걸리는 시간(ms)
        arrows : true,         // 옆으로 이동하는 화살표 표시 여부
        dots : true,         // 스크롤바 아래 점으로 페이지네이션 여부
        fade : true,        // fade 효과
        speed : 700,
        autoplay : true,            // 자동 스크롤 사용 여부
        autoplaySpeed : 2000,         // 자동 스크롤 시 다음으로 넘어가는데 걸리는 시간 (ms)
        pauseOnHover : true,        // 슬라이드 이동    시 마우스 호버하면 슬라이더 멈추게 설정
        vertical : false,        // 세로 방향 슬라이드 옵션
        prevArrow : "<button type='button' class='slick-prev'>Previous</button>",        // 이전 화살표 모양 설정
        nextArrow : "<button type='button' class='slick-next'>Next</button>",        // 다음 화살표 모양 설정
        dotsClass : "slick-dots",     //아래 나오는 페이지네이션(점) css class 지정
        draggable : true,     //드래그 가능 여부


    });
  })

function searchInput() {
    let searchValue = $('#searchInput').val().trim()
    if (searchValue.length > 1) {
        location.href = "search/" + searchValue + "/";
        console.log(searchValue);
    } else {
        alert('검색어가 너무 짧습니다.')
    }
}
$(document).ready(function(){
    $('#searchInput').on('keyup', function(event){
        if(event.key == 'Enter'){
            searchInput();
        }
    })
})