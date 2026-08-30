package com.supersete.talov2;

import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.provider.OpenableColumns;
import android.database.Cursor;
import android.widget.Button;
import android.widget.ProgressBar;
import android.widget.TextView;

import com.chaquo.python.PyObject;
import com.chaquo.python.Python;
import com.chaquo.python.android.AndroidPlatform;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

public class MainActivity extends Activity {
    private static final int PICK_FILE = 1001;
    private Uri fileUri;
    private TextView status;
    private ProgressBar progress;
    private final ExecutorService executor = Executors.newSingleThreadExecutor();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        if (!Python.isStarted()) {
            Python.start(new AndroidPlatform(this));
        }

        Button btnArquivo = findViewById(R.id.btnArquivo);
        Button btnAnalisar = findViewById(R.id.btnAnalisar);
        status = findViewById(R.id.status);
        progress = findViewById(R.id.progresso);

        btnArquivo.setOnClickListener(v -> {
            Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
            i.addCategory(Intent.CATEGORY_OPENABLE);
            i.setType("text/*");
            startActivityForResult(i, PICK_FILE);
        });

        btnAnalisar.setOnClickListener(v -> {
            if (fileUri == null) {
                status.setText("Selecione primeiro o arquivo TXT do Super Sete.");
                return;
            }
            progress.setProgress(5);
            status.setText("Lendo histórico...");
            executor.submit(() -> {
                try {
                    String text = readText(fileUri);
                    runOnUiThread(() -> { progress.setProgress(25); status.setText("Estudando comportamento das repetidas..."); });
                    Python py = Python.getInstance();
                    PyObject mod = py.getModule("motor_super_sete_v2");
                    PyObject result = mod.callAttr("analisar_texto", text);
                    String out = result.toString();
                    runOnUiThread(() -> { progress.setProgress(100); status.setText(out); });
                } catch (Exception e) {
                    runOnUiThread(() -> { progress.setProgress(0); status.setText("ERRO: " + e.getMessage()); });
                }
            });
        });
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (requestCode == PICK_FILE && resultCode == RESULT_OK && data != null) {
            fileUri = data.getData();
            if (fileUri != null) {
                getContentResolver().takePersistableUriPermission(fileUri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                status.setText("Arquivo selecionado: " + getDisplayName(fileUri));
            }
        }
    }

    private String getDisplayName(Uri uri) {
        try (Cursor c = getContentResolver().query(uri, null, null, null, null)) {
            if (c != null && c.moveToFirst()) {
                int idx = c.getColumnIndex(OpenableColumns.DISPLAY_NAME);
                if (idx >= 0) return c.getString(idx);
            }
        }
        return uri.toString();
    }

    private String readText(Uri uri) throws Exception {
        try (InputStream in = getContentResolver().openInputStream(uri); ByteArrayOutputStream out = new ByteArrayOutputStream()) {
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) != -1) out.write(buf, 0, n);
            return out.toString("UTF-8");
        }
    }
}
