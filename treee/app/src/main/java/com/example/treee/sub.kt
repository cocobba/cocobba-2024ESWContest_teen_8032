package com.example.treee

import android.content.Intent
import android.os.Bundle
import android.widget.Button
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity

class sub : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.login)

        // 버튼을 코드에서 찾아서 클릭 리스너를 설정합니다.
        val loginButton: Button = findViewById(R.id.button_login)

        loginButton.setOnClickListener {
            // 토스트 메시지 표시
            Toast.makeText(this, "로그인 버튼 클릭됨", Toast.LENGTH_SHORT).show()

            // MainActivity로 이동하는 Intent 생성
            val intent = Intent(this, MainActivity::class.java)
            startActivity(intent)  // 액티비티 시작
        }
    }
}
