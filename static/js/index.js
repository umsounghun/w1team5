// index 페이지 내에서 사용할 함수 정의.
/**
 * 키워드 검색
 * 전달받은 검색어 기준으로 해당 되는 카드만 재구성하도록 작업
 */
function keyword_fillter(keyword)
{
    const classnm = document.getElementsByClassName("card_desc");
    const delarea = document.getElementsByClassName("card_arr");

    for(let i=0; i < classnm.length; i++)
    {
        let can_nm = classnm[i].getElementsByClassName('c_name');
        let can_symbol = classnm[i].getElementsByClassName('c_symbol');
        let can_party = classnm[i].getElementsByClassName('c_party');

        if(can_nm[0].innerHTML.toLowerCase().indexOf(keyword) != -1)
        {
            delarea[i].style.display = "flex";
        }
        else
            delarea[i].style.display = "none";
        console.log(can_nm,can_symbol,can_party)
    }
    console.log(keyword);

}