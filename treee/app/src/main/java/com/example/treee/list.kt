package com.example.treee

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.location.Location
import android.net.Uri
import android.os.Bundle
import android.widget.Button
import android.widget.ImageButton
import android.widget.ImageView
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.google.android.gms.location.FusedLocationProviderClient
import com.google.android.gms.location.LocationServices
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.RequestBody.Companion.asRequestBody
import java.io.File
import java.io.IOException

class list : AppCompatActivity() {

    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private val client = OkHttpClient()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.list)

        // FusedLocationProviderClient 초기화
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)

        val imagePaths = intent.getStringArrayListExtra("image_paths")
        val layout: LinearLayout = findViewById(R.id.imageContainer)
        val sendButton: Button = findViewById(R.id.button_send)

        imagePaths?.forEach { imagePath ->
            val imageView = ImageView(this)
            imageView.layoutParams = LinearLayout.LayoutParams(
                500,  // Width in dp
                500   // Height in dp
            )
            imageView.scaleType = ImageView.ScaleType.CENTER_CROP
            imageView.setImageURI(Uri.fromFile(File(imagePath)))
            layout.addView(imageView)
        }
        val viewMapImageButton: ImageButton = findViewById(R.id.map)
        viewMapImageButton.setOnClickListener {
            Toast.makeText(this, "지도 버튼 클릭됨", Toast.LENGTH_SHORT).show()
            val intent = Intent(Intent.ACTION_VIEW)
            intent.data = Uri.parse("http://59.15.198.238:8080")
            startActivity(intent)
        }
        sendButton.setOnClickListener {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                // 위치 권한이 부여되지 않은 경우 권한 요청
                ActivityCompat.requestPermissions(this, arrayOf(Manifest.permission.ACCESS_FINE_LOCATION), 1)
            } else {
                // 위치 권한이 부여된 경우 위치 정보를 가져옴
                getLastLocationAndUpload(imagePaths)
            }
        }
    }

    private fun getLastLocationAndUpload(imagePaths: ArrayList<String>?) {
        try {
            fusedLocationClient.lastLocation
                .addOnSuccessListener { location: Location? ->
                    if (location != null) {
                        val latitude = location.latitude
                        val longitude = location.longitude

                        imagePaths?.forEach { imagePath ->
                            uploadImageToServer(imagePath, latitude, longitude)
                        }
                    } else {
                        Toast.makeText(this, "위치를 가져올 수 없습니다.", Toast.LENGTH_SHORT).show()
                    }
                }
        } catch (e: SecurityException) {
            e.printStackTrace()
            Toast.makeText(this, "위치 권한이 필요합니다.", Toast.LENGTH_SHORT).show()
        }
    }

    private fun uploadImageToServer(imagePath: String, latitude: Double, longitude: Double) {
        val file = File(imagePath)
        val mediaType = "image/jpeg".toMediaTypeOrNull()
        val requestBody = MultipartBody.Builder()
            .setType(MultipartBody.FORM)
            .addFormDataPart("file", file.name, file.asRequestBody(mediaType))
            .addFormDataPart("latitude", latitude.toString())
            .addFormDataPart("longitude", longitude.toString())
            .build()

        val request = Request.Builder()
            .url("http://59.15.198.238:8080/upload")
            .post(requestBody)
            .build()

        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                runOnUiThread {
                    Toast.makeText(this@list, "전송 실패: ${e.message}", Toast.LENGTH_SHORT).show()
                    e.printStackTrace()
                }
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    runOnUiThread {
                        Toast.makeText(this@list, "전송 성공", Toast.LENGTH_SHORT).show()
                    }
                } else {
                    runOnUiThread {
                        Toast.makeText(this@list, "전송 실패: ${response.message}", Toast.LENGTH_SHORT).show()
                    }
                }
            }
        })
    }

    // 권한 요청 결과 처리
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == 1 && grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            // 권한이 허용된 경우 위치 정보 가져오기 시도
            getLastLocationAndUpload(intent.getStringArrayListExtra("image_paths"))
        } else {
            Toast.makeText(this, "위치 권한이 필요합니다.", Toast.LENGTH_SHORT).show()
        }
    }
}
