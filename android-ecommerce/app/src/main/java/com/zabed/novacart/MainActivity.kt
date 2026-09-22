package com.zabed.novacart

import android.app.*
import android.os.*
import android.graphics.Color
import android.view.*
import android.widget.*
import org.json.JSONArray
import java.net.HttpURLConnection
import java.net.URL
import kotlin.concurrent.thread

data class Product(val id:Int,val name:String,val price:Double,val category:String,val stock:Int,val image:String)

class MainActivity : Activity() {
    private val api = "https://novacart-web-production.up.railway.app/api/products"
    private lateinit var list: LinearLayout
    private lateinit var progress: ProgressBar
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val root=LinearLayout(this); root.orientation=LinearLayout.VERTICAL; root.setBackgroundColor(Color.rgb(245,247,250))
        val bar=TextView(this); bar.text="🛒  NovaCart"; bar.textSize=24f; bar.setTextColor(Color.WHITE); bar.setPadding(24,24,24,24); bar.setBackgroundColor(Color.rgb(49,94,251))
        root.addView(bar,LinearLayout.LayoutParams(-1,70))
        progress=ProgressBar(this); root.addView(progress,LinearLayout.LayoutParams(-1,80))
        list=LinearLayout(this); list.orientation=LinearLayout.VERTICAL; list.setPadding(16,8,16,20)
        val scroll=ScrollView(this); scroll.addView(list); root.addView(scroll,LinearLayout.LayoutParams(-1,0,1f))
        setContentView(root); loadProducts()
    }
    private fun loadProducts(){
        thread {
            try {
                val c=URL(api).openConnection() as HttpURLConnection
                c.requestMethod="GET"; c.connectTimeout=10000; c.readTimeout=10000
                val body=c.inputStream.bufferedReader().use{it.readText()}; c.disconnect()
                val arr=JSONArray(org.json.JSONObject(body).getJSONArray("products").toString())
                val products=mutableListOf<Product>()
                for(i in 0 until arr.length()){val p=arr.getJSONObject(i); products.add(Product(p.getInt("id"),p.getString("name"),p.getDouble("price"),p.getString("category"),p.getInt("stock"),p.optString("image","")))}
                runOnUiThread{progress.visibility=View.GONE; render(products)}
            } catch(err:Exception){runOnUiThread{progress.visibility=View.GONE; val t=TextView(this);t.text="Could not load products.\n"+err.message;t.textSize=16f;t.setPadding(20,30,20,20);list.addView(t)}}
        }
    }
    private fun render(products:List<Product>){
        if(products.isEmpty()){val t=TextView(this);t.text="No products available.";list.addView(t);return}
        products.forEach{p->
            val card=LinearLayout(this);card.orientation=LinearLayout.VERTICAL;card.setPadding(22,18,22,18);card.setBackgroundColor(Color.WHITE)
            val title=TextView(this);title.text=p.name;title.textSize=19f;title.setTextColor(Color.rgb(25,35,50))
            val info=TextView(this);info.text=p.category+"  •  Stock: "+p.stock+"\n$"+String.format("%.2f",p.price);info.textSize=16f;info.setPadding(0,8,0,12)
            val btn=Button(this);btn.text="Add to Cart";btn.setOnClickListener{Toast.makeText(this,p.name+" added to cart",Toast.LENGTH_SHORT).show()}
            card.addView(title);card.addView(info);card.addView(btn)
            val lp=LinearLayout.LayoutParams(-1,LinearLayout.LayoutParams.WRAP_CONTENT);lp.setMargins(0,0,0,16);list.addView(card,lp)
        }
    }
}
