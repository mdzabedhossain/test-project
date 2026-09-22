package com.zabed.facescanstore

import android.Manifest
import android.app.*
import android.os.*
import android.content.pm.PackageManager
import android.graphics.Color
import android.graphics.ImageFormat
import android.hardware.camera2.*
import android.media.ImageReader
import android.view.*
import android.widget.*
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*
import kotlin.concurrent.thread

class MainActivity: Activity(){
 private lateinit var preview:TextureView
 private lateinit var info:TextView
 private var camera:CameraDevice?=null
 private var reader:ImageReader?=null
 private var session:CameraCaptureSession?=null
 private val request=10
 override fun onCreate(b:Bundle?){super.onCreate(b);buildUi();if(checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)requestPermissions(arrayOf(Manifest.permission.CAMERA),request)else openCamera()}
 private fun buildUi(){
  val root=LinearLayout(this);root.orientation=LinearLayout.VERTICAL
  val title=TextView(this);title.text="Face Scan Store";title.textSize=24f;title.setPadding(24,22,24,22);title.setTextColor(Color.WHITE);title.setBackgroundColor(Color.rgb(49,94,251));root.addView(title)
  preview=TextureView(this);root.addView(preview,LinearLayout.LayoutParams(-1,0,1f))
  val row=LinearLayout(this);row.setPadding(12,8,12,8)
  val scan=Button(this);scan.text="📸 Scan & Store Face";scan.setOnClickListener{capture()};row.addView(scan,LinearLayout.LayoutParams(0,60,1f))
  val stored=Button(this);stored.text="Stored";stored.setOnClickListener{showStored()};row.addView(stored,LinearLayout.LayoutParams(0,60,1f));root.addView(row)
  info=TextView(this);info.text="Scans stay in this app's private storage.";info.setPadding(18,8,18,18);root.addView(info);setContentView(root)
 }
 override fun onRequestPermissionsResult(r:Int,p:Array<String>,g:IntArray){super.onRequestPermissionsResult(r,p,g);if(r==request&&g.isNotEmpty()&&g[0]==PackageManager.PERMISSION_GRANTED)openCamera()else info.text="Camera permission is required."}
 private fun openCamera(){
  val cm=getSystemService(CameraManager::class.java);val id=cm.cameraIdList.firstOrNull()?:return
  reader=ImageReader.newInstance(1080,1920,ImageFormat.JPEG,2)
  reader!!.setOnImageAvailableListener({ir->val image=ir.acquireLatestImage()?:return@setOnImageAvailableListener;val buf=image.planes[0].buffer;val bytes=ByteArray(buf.remaining());buf.get(bytes);image.close();thread{val dir=File(filesDir,"faces");dir.mkdirs();val name="face_"+SimpleDateFormat("yyyyMMdd_HHmmss",Locale.US).format(Date())+".jpg";FileOutputStream(File(dir,name)).use{it.write(bytes)};runOnUiThread{info.text="Stored: $name"} }},null)
  if(checkSelfPermission(Manifest.permission.CAMERA)!=PackageManager.PERMISSION_GRANTED)return
  cm.openCamera(id,object:CameraDevice.StateCallback(){
   override fun onOpened(c:CameraDevice){camera=c;preview.surfaceTextureListener=object:TextureView.SurfaceTextureListener{
    override fun onSurfaceTextureAvailable(s:android.graphics.SurfaceTexture,w:Int,h:Int){startPreview(s)}
    override fun onSurfaceTextureSizeChanged(s:android.graphics.SurfaceTexture,w:Int,h:Int){}
    override fun onSurfaceTextureDestroyed(s:android.graphics.SurfaceTexture)=true
    override fun onSurfaceTextureUpdated(s:android.graphics.SurfaceTexture){}
   };if(preview.isAvailable)startPreview(preview.surfaceTexture)}
   override fun onDisconnected(c:CameraDevice){c.close()}
   override fun onError(c:CameraDevice,e:Int){c.close()}
  },null)
 }
 private fun startPreview(t:android.graphics.SurfaceTexture){t.setDefaultBufferSize(preview.width,preview.height);val ps=Surface(t);val cap=camera!!.createCaptureRequest(CameraDevice.TEMPLATE_PREVIEW);cap.addTarget(ps);camera!!.createCaptureSession(listOf(ps),object:CameraCaptureSession.StateCallback(){override fun onConfigured(s:CameraCaptureSession){session=s;s.setRepeatingRequest(cap.build(),null,null)};override fun onConfigureFailed(s:CameraCaptureSession){}},null)}
 private fun capture(){val r=reader?:return;val c=camera?:return;val cap=c.createCaptureRequest(CameraDevice.TEMPLATE_STILL_CAPTURE);cap.addTarget(r.surface);session?.capture(cap.build(),null,null)}
 private fun showStored(){val d=File(filesDir,"faces");val names=d.list()?.sortedDescending()?:emptyArray();AlertDialog.Builder(this).setTitle("Stored face scans").setMessage(if(names.isEmpty())"No scans stored." else names.joinToString("\n")).setPositiveButton("OK",null).show()}
 override fun onDestroy(){session?.close();camera?.close();reader?.close();super.onDestroy()}
}
