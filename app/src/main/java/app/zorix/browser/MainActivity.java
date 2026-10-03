package app.zorix.browser;

import android.app.Activity;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.os.Build;
import android.os.Bundle;
import android.text.InputType;
import android.view.Gravity;
import android.view.KeyEvent;
import android.view.View;
import android.view.ViewGroup;
import android.view.inputmethod.EditorInfo;
import android.view.inputmethod.InputMethodManager;
import android.content.Context;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.PopupMenu;
import android.widget.ProgressBar;
import android.widget.TextView;

import org.mozilla.geckoview.GeckoRuntime;
import org.mozilla.geckoview.GeckoSession;
import org.mozilla.geckoview.GeckoView;

import java.net.URLEncoder;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {
    private static final int BG = Color.rgb(247, 247, 245);
    private static final int SURFACE = Color.WHITE;
    private static final int TEXT = Color.rgb(17, 17, 17);
    private static final int MUTED = Color.rgb(105, 105, 100);
    private static final int BORDER = Color.rgb(229, 229, 225);

    private static GeckoRuntime runtime;

    private GeckoSession session;
    private GeckoView geckoView;
    private FrameLayout browserFrame;
    private LinearLayout homePanel;
    private EditText addressBar;
    private ProgressBar progressBar;
    private TextView backButton;
    private TextView forwardButton;
    private boolean canGoBack;
    private boolean canGoForward;
    private boolean onHome = true;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        configureWindow();
        setContentView(buildUi());
        startGecko();

        String incoming = getIntent() != null ? getIntent().getDataString() : null;
        if (incoming != null && !incoming.isBlank()) {
            navigate(incoming);
        } else {
            showHome();
        }
    }

    private void configureWindow() {
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        int flags = 0;
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            flags |= View.SYSTEM_UI_FLAG_LIGHT_STATUS_BAR;
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            flags |= View.SYSTEM_UI_FLAG_LIGHT_NAVIGATION_BAR;
        }
        getWindow().getDecorView().setSystemUiVisibility(flags);
    }

    private View buildUi() {
        LinearLayout root = new LinearLayout(this);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setBackgroundColor(BG);

        LinearLayout top = new LinearLayout(this);
        top.setOrientation(LinearLayout.HORIZONTAL);
        top.setGravity(Gravity.CENTER_VERTICAL);
        top.setPadding(dp(12), dp(10), dp(12), dp(8));
        root.addView(top, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView mark = new TextView(this);
        mark.setText("Z");
        mark.setTextColor(Color.WHITE);
        mark.setTextSize(16);
        mark.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        mark.setGravity(Gravity.CENTER);
        mark.setBackground(roundRect(TEXT, 14, TEXT, 0));
        LinearLayout.LayoutParams markParams = new LinearLayout.LayoutParams(dp(38), dp(38));
        markParams.setMarginEnd(dp(10));
        top.addView(mark, markParams);
        mark.setOnClickListener(v -> showHome());

        addressBar = new EditText(this);
        addressBar.setSingleLine(true);
        addressBar.setHint("Search or enter address");
        addressBar.setHintTextColor(MUTED);
        addressBar.setTextColor(TEXT);
        addressBar.setTextSize(15);
        addressBar.setPadding(dp(16), 0, dp(16), 0);
        addressBar.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        addressBar.setImeOptions(EditorInfo.IME_ACTION_GO);
        addressBar.setBackground(roundRect(SURFACE, 22, BORDER, 1));
        LinearLayout.LayoutParams addressParams = new LinearLayout.LayoutParams(0, dp(44), 1f);
        top.addView(addressBar, addressParams);

        TextView menu = iconButton("⋯", "Menu");
        LinearLayout.LayoutParams menuParams = new LinearLayout.LayoutParams(dp(44), dp(44));
        menuParams.setMarginStart(dp(8));
        top.addView(menu, menuParams);
        menu.setOnClickListener(this::showMenu);

        addressBar.setOnEditorActionListener((v, actionId, event) -> {
            boolean keyboardGo = actionId == EditorInfo.IME_ACTION_GO
                    || (event != null && event.getKeyCode() == KeyEvent.KEYCODE_ENTER
                    && event.getAction() == KeyEvent.ACTION_DOWN);
            if (keyboardGo) {
                navigate(addressBar.getText().toString());
                return true;
            }
            return false;
        });
        addressBar.setOnFocusChangeListener((v, focused) -> {
            if (focused && !addressBar.getText().toString().isBlank()) {
                addressBar.selectAll();
            }
        });

        progressBar = new ProgressBar(this, null, android.R.attr.progressBarStyleHorizontal);
        progressBar.setMax(100);
        progressBar.setProgress(0);
        progressBar.setVisibility(View.INVISIBLE);
        root.addView(progressBar, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(2)));

        browserFrame = new FrameLayout(this);
        browserFrame.setBackgroundColor(BG);
        root.addView(browserFrame, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, 0, 1f));

        geckoView = new GeckoView(this);
        browserFrame.addView(geckoView, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        homePanel = buildHomePanel();
        browserFrame.addView(homePanel, new FrameLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));

        LinearLayout bottom = new LinearLayout(this);
        bottom.setGravity(Gravity.CENTER);
        bottom.setPadding(dp(12), dp(8), dp(12), dp(12));
        bottom.setOrientation(LinearLayout.HORIZONTAL);
        root.addView(bottom, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        backButton = iconButton("‹", "Back");
        forwardButton = iconButton("›", "Forward");
        TextView home = iconButton("⌂", "Home");
        TextView refresh = iconButton("↻", "Reload");

        addBottomButton(bottom, backButton);
        addBottomButton(bottom, forwardButton);
        addBottomButton(bottom, home);
        addBottomButton(bottom, refresh);

        backButton.setOnClickListener(v -> {
            if (!onHome && canGoBack) {
                session.goBack();
            } else {
                showHome();
            }
        });
        forwardButton.setOnClickListener(v -> {
            if (!onHome && canGoForward) {
                session.goForward();
            }
        });
        home.setOnClickListener(v -> showHome());
        refresh.setOnClickListener(v -> {
            if (onHome) {
                addressBar.requestFocus();
                showKeyboard(addressBar);
            } else {
                session.reload();
            }
        });

        updateNavigationButtons();
        return root;
    }

    private LinearLayout buildHomePanel() {
        LinearLayout home = new LinearLayout(this);
        home.setOrientation(LinearLayout.VERTICAL);
        home.setGravity(Gravity.CENTER_HORIZONTAL);
        home.setPadding(dp(28), dp(56), dp(28), dp(24));
        home.setBackgroundColor(BG);

        TextView title = new TextView(this);
        title.setText("Zorix");
        title.setTextColor(TEXT);
        title.setTextSize(42);
        title.setTypeface(Typeface.create("sans", Typeface.BOLD));
        title.setGravity(Gravity.CENTER);
        home.addView(title, new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));

        TextView subtitle = new TextView(this);
        subtitle.setText("A quiet place to browse.");
        subtitle.setTextColor(MUTED);
        subtitle.setTextSize(16);
        subtitle.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams subtitleParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        subtitleParams.topMargin = dp(8);
        home.addView(subtitle, subtitleParams);

        EditText heroSearch = new EditText(this);
        heroSearch.setSingleLine(true);
        heroSearch.setHint("Ask the web anything");
        heroSearch.setHintTextColor(MUTED);
        heroSearch.setTextColor(TEXT);
        heroSearch.setTextSize(17);
        heroSearch.setPadding(dp(18), 0, dp(18), 0);
        heroSearch.setImeOptions(EditorInfo.IME_ACTION_GO);
        heroSearch.setBackground(roundRect(SURFACE, 26, BORDER, 1));
        LinearLayout.LayoutParams searchParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, dp(56));
        searchParams.topMargin = dp(34);
        home.addView(heroSearch, searchParams);

        heroSearch.setOnEditorActionListener((v, actionId, event) -> {
            if (actionId == EditorInfo.IME_ACTION_GO
                    || (event != null && event.getKeyCode() == KeyEvent.KEYCODE_ENTER)) {
                String value = heroSearch.getText().toString();
                addressBar.setText(value);
                navigate(value);
                heroSearch.setText("");
                return true;
            }
            return false;
        });

        LinearLayout quickRow = new LinearLayout(this);
        quickRow.setOrientation(LinearLayout.HORIZONTAL);
        quickRow.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams quickParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        quickParams.topMargin = dp(18);
        home.addView(quickRow, quickParams);

        TextView openai = pill("OpenAI");
        TextView github = pill("GitHub");
        TextView wikipedia = pill("Wikipedia");
        quickRow.addView(openai);
        quickRow.addView(github);
        quickRow.addView(wikipedia);

        openai.setOnClickListener(v -> navigate("https://openai.com"));
        github.setOnClickListener(v -> navigate("https://github.com"));
        wikipedia.setOnClickListener(v -> navigate("https://wikipedia.org"));

        TextView footer = new TextView(this);
        footer.setText("Gecko-powered · no Android WebView");
        footer.setTextColor(MUTED);
        footer.setTextSize(12);
        footer.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams footerParams = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        footerParams.topMargin = dp(28);
        home.addView(footer, footerParams);

        return home;
    }

    private void startGecko() {
        if (runtime == null) {
            runtime = GeckoRuntime.create(this);
        }

        session = new GeckoSession();
        session.setContentDelegate(new GeckoSession.ContentDelegate() {});
        session.setNavigationDelegate(new GeckoSession.NavigationDelegate() {
            @Override
            public void onCanGoBack(GeckoSession geckoSession, boolean value) {
                canGoBack = value;
                updateNavigationButtons();
            }

            @Override
            public void onCanGoForward(GeckoSession geckoSession, boolean value) {
                canGoForward = value;
                updateNavigationButtons();
            }
        });
        session.setProgressDelegate(new GeckoSession.ProgressDelegate() {
            @Override
            public void onPageStart(GeckoSession geckoSession, String url) {
                onHome = false;
                homePanel.setVisibility(View.GONE);
                geckoView.setVisibility(View.VISIBLE);
                progressBar.setVisibility(View.VISIBLE);
                progressBar.setProgress(8);
                if (url != null && !url.startsWith("about:")) {
                    addressBar.setText(url);
                }
            }

            @Override
            public void onProgressChange(GeckoSession geckoSession, int progress) {
                progressBar.setVisibility(View.VISIBLE);
                progressBar.setProgress(progress);
            }

            @Override
            public void onPageStop(GeckoSession geckoSession, boolean success) {
                progressBar.setProgress(100);
                progressBar.postDelayed(() -> progressBar.setVisibility(View.INVISIBLE), 180);
            }
        });

        session.open(runtime);
        geckoView.setSession(session);
    }

    private void navigate(String raw) {
        if (session == null) return;
        String target = normalizeInput(raw);
        if (target == null) return;
        hideKeyboard();
        addressBar.clearFocus();
        onHome = false;
        homePanel.setVisibility(View.GONE);
        geckoView.setVisibility(View.VISIBLE);
        addressBar.setText(target);
        session.loadUri(target);
    }

    private String normalizeInput(String raw) {
        if (raw == null) return null;
        String value = raw.trim();
        if (value.isEmpty()) return null;

        String lower = value.toLowerCase();
        if (lower.startsWith("http://") || lower.startsWith("https://")
                || lower.startsWith("about:") || lower.startsWith("data:")) {
            return value;
        }

        if (!value.contains(" ") && (value.contains(".") || value.startsWith("localhost"))) {
            return "https://" + value;
        }

        return "https://www.google.com/search?q="
                + URLEncoder.encode(value, StandardCharsets.UTF_8);
    }

    private void showHome() {
        onHome = true;
        geckoView.setVisibility(View.GONE);
        homePanel.setVisibility(View.VISIBLE);
        addressBar.setText("");
        progressBar.setVisibility(View.INVISIBLE);
        hideKeyboard();
        updateNavigationButtons();
    }

    private void showMenu(View anchor) {
        PopupMenu popup = new PopupMenu(this, anchor);
        popup.getMenu().add("New start page");
        popup.getMenu().add("Open OpenAI");
        popup.getMenu().add("About Zorix");
        popup.setOnMenuItemClickListener(item -> {
            String title = item.getTitle().toString();
            if (title.equals("New start page")) {
                showHome();
            } else if (title.equals("Open OpenAI")) {
                navigate("https://openai.com");
            } else {
                showAbout();
            }
            return true;
        });
        popup.show();
    }

    private void showAbout() {
        onHome = true;
        geckoView.setVisibility(View.GONE);
        homePanel.setVisibility(View.VISIBLE);
        if (homePanel.getChildCount() > 0 && homePanel.getChildAt(0) instanceof TextView) {
            ((TextView) homePanel.getChildAt(0)).setText("Zorix");
        }
        addressBar.setText("");
    }

    private void updateNavigationButtons() {
        if (backButton == null || forwardButton == null) return;
        backButton.setAlpha(onHome || !canGoBack ? 0.35f : 1f);
        forwardButton.setAlpha(onHome || !canGoForward ? 0.35f : 1f);
    }

    private TextView iconButton(String symbol, String description) {
        TextView button = new TextView(this);
        button.setText(symbol);
        button.setContentDescription(description);
        button.setTextColor(TEXT);
        button.setTextSize(26);
        button.setGravity(Gravity.CENTER);
        button.setBackground(roundRect(SURFACE, 18, BORDER, 1));
        button.setFocusable(true);
        button.setClickable(true);
        return button;
    }

    private TextView pill(String text) {
        TextView pill = new TextView(this);
        pill.setText(text);
        pill.setTextColor(TEXT);
        pill.setTextSize(13);
        pill.setGravity(Gravity.CENTER);
        pill.setPadding(dp(14), 0, dp(14), 0);
        pill.setBackground(roundRect(SURFACE, 18, BORDER, 1));
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.WRAP_CONTENT, dp(36));
        params.setMargins(dp(4), 0, dp(4), 0);
        pill.setLayoutParams(params);
        return pill;
    }

    private void addBottomButton(LinearLayout row, TextView button) {
        LinearLayout.LayoutParams params = new LinearLayout.LayoutParams(0, dp(48), 1f);
        params.setMargins(dp(5), 0, dp(5), 0);
        row.addView(button, params);
    }

    private GradientDrawable roundRect(int fill, float radiusDp, int stroke, int strokeDp) {
        GradientDrawable drawable = new GradientDrawable();
        drawable.setColor(fill);
        drawable.setCornerRadius(dp(radiusDp));
        if (strokeDp > 0) {
            drawable.setStroke(dp(strokeDp), stroke);
        }
        return drawable;
    }

    private int dp(float value) {
        return (int) (value * getResources().getDisplayMetrics().density + 0.5f);
    }

    private void hideKeyboard() {
        View focus = getCurrentFocus();
        if (focus != null) {
            InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.hideSoftInputFromWindow(focus.getWindowToken(), 0);
        }
    }

    private void showKeyboard(View view) {
        view.requestFocus();
        view.post(() -> {
            InputMethodManager imm = (InputMethodManager) getSystemService(Context.INPUT_METHOD_SERVICE);
            imm.showSoftInput(view, InputMethodManager.SHOW_IMPLICIT);
        });
    }

    @Override
    public void onBackPressed() {
        if (!onHome && canGoBack) {
            session.goBack();
        } else if (!onHome) {
            showHome();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onDestroy() {
        if (session != null) {
            session.close();
        }
        super.onDestroy();
    }
}
