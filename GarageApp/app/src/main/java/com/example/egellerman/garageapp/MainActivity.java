package com.example.egellerman.garageapp;

import android.os.Handler;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.EditText;
import android.widget.TextView;
import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;

import static android.provider.AlarmClock.EXTRA_MESSAGE;

public class MainActivity extends AppCompatActivity {

    private TextView mTextViewReplyFromServer;
    private EditText mEditTextSendMessage;
    public static final String EXTRA_MESSAGE = "com.example.myfirstapp.MESSAGE";
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
    }

    public void sendMessage(View view) {
        //final Intent intent = new Intent(this, DisplayMessageActivity.class);
        EditText editText = (EditText) findViewById(R.id.editText);
        final String message = editText.getText().toString();
        //intent.putExtra(EXTRA_MESSAGE, message);
        //startActivity(intent);

        transmitToServer(message);
    }

    public void zeroDoorStatus(View view){
        final String message = ("0,status");
        transmitToServer(message);
    }

    public void oneDoorStatus(View view){
        final String message = ("1,status");
        transmitToServer(message);
    }

    public void zeroDoorOpen(View view){
        final String message = ("0,open");
        transmitToServer(message);
    }

    public void oneDoorOpen(View view){
        final String message = ("1,open");
        transmitToServer(message);
    }

    public void zeroDoorClose(View view){
        final String message = ("0,close");
        transmitToServer(message);
    }

    public void oneDoorClose(View view){
        final String message = ("1,close");
        transmitToServer(message);
    }

    public void updateServerTextView(String toThis) {
        TextView textView = findViewById(R.id.serverTextView);
        textView.setText(toThis);
    }

    public void transmitToServer(final String message){
        final Handler handler = new Handler();
        Thread thread = new Thread(new Runnable() {
            @Override
            public void run() {

                try {
                    Socket s = new Socket("192.168.1.100", 9001);
                    DataInputStream is = new DataInputStream(s.getInputStream());
                    DataOutputStream os = new DataOutputStream(s.getOutputStream());
                    String passphrase = "2C9EC7BA1FCA4534186DD8082571D547ADA2A6B4E8C5BCC9AA0E093CCFC69BB7";
                    //Log.d("CREATION","Test message 1");
                    os.writeBytes(passphrase);
                    Log.d("CREATION",passphrase);
                    //os.flush();
                    //String line = is.readLine();
                    int read;
                    byte[] buffer = new byte[1024];
                    String output = "";
                    while((read = is.read(buffer)) != -1){
                        String data = new String(buffer, 0, read);
                        //Log.d("CREATION",data);
                        //Log.d("CREATION","Read value: " + read);
                        output = output + data;
                        //Log.d("CREATION","Read value: " + read);
                        //buffer = null;
                        break;
                    }
                    Log.d("CREATION",output);
                    byte[] buffer2 = new byte[1024];
                    String output2 = "";
                    //os.flush();
                    if(output.equals("OK")){
                        //Log.d("CREATION",message);
                        DataOutputStream os2 = new DataOutputStream(s.getOutputStream());
                        os2.writeBytes(message);
                        while((read = is.read(buffer2)) != -1){
                            String data = new String(buffer2, 0, read);
                            //Log.d("Output",data);
                            output2 += data;
                            //buffer = null;
                            break;
                        }
                        final String sendOutput = output2;

                        runOnUiThread(new Runnable() {
                            @Override
                            public void run() {

                                //Updates the UI
                                updateServerTextView(sendOutput);
                            }
                        });

                        Log.d("CREATION",output2);
                    }
                    s.close();
                } catch (IOException e) {
                    e.printStackTrace();
                }
            }
        });

        thread.start();
    }

}
