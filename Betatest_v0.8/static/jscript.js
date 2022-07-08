function moveCursora(tel) {
    if (tel.value.length == 3) {
        document.getElementById("phonenum1").focus();
    }
}
function moveCursorb(telbox) {
    if (telbox.value.length == 4) {
        document.getElementById("phonenum2").focus();
    }
}

let q1 = document.getElementById('phonenum');
function final() {
    document.getElementById("submit_button").innerHTML = "제출 완료";
    var formData1 = $('#form1').serializeArray()
    var formData2 = $('#form2').serializeArray()
    var postdata = {
        ID, 'formData1':formData1, 'formData2':formData2
    }
    console.log(postdata)

    $.ajax({
        type: 'POST',
        url: '{{url_for("ajax")}}',
        data: JSON.stringify(postdata),
        dataType : 'JSON',
        contentType: "application/json",
        success: function(data){
            console.log(postdata)
            alert('성공! ' + JSON.stringify(postdata))
        },
        error: function(request, status, error){
            alert('ajax 통신 실패')
            alert(error);
        }
    })
}
$('#execute').click(function(){
    var id = $('#id1').val();

    var postdata = {
        'id':id
    }
    $.ajax({
        type: 'POST',
        url: '{{url_for("ajax")}}',
        data: JSON.stringify(postdata),
        dataType : 'JSON',
        contentType: "application/json",
        success: function(data){
            alert('성공!' + data.result2['id'])
        },
        error: function(request, status, error){
            alert('ajax 통신 실패')
            alert(error);
        }
    })
})