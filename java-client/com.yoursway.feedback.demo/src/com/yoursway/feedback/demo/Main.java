package com.yoursway.feedback.demo;

import org.eclipse.swt.SWT;
import org.eclipse.swt.events.SelectionAdapter;
import org.eclipse.swt.events.SelectionEvent;
import org.eclipse.swt.layout.GridData;
import org.eclipse.swt.layout.GridLayout;
import org.eclipse.swt.widgets.Button;
import org.eclipse.swt.widgets.Display;
import org.eclipse.swt.widgets.Shell;

import com.yoursway.feedback.Detail;
import com.yoursway.feedback.FeedbackConfiguration;
import com.yoursway.feedback.FeedbackEngine;

public class Main {

	public static final FeedbackEngine FEEDBACK = new FeedbackConfiguration(
			"FuckUpper", "0.99a.N20090216", "feedback.yoursway.com",
			"fuckupper").create();

	public static void main(String[] args) {
		Display display = new Display();
		Shell shell = new Shell(display);
		shell.setLayout(new GridLayout(1, false));

		Button button = new Button(shell, SWT.PUSH);
		button.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false,
				false));
		button.setText("Fuck up");
		button.addSelectionListener(new SelectionAdapter() {
			public void widgetSelected(SelectionEvent e) {
				throw new IllegalArgumentException("Fuck.");
			}
		});

		final Button button2 = new Button(shell, SWT.PUSH);
		button2.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false,
				false));
		button2.setText("Go nuts");
		button2.addSelectionListener(new SelectionAdapter() {
			public void widgetSelected(SelectionEvent e) {
				button2.setText(null);
			}
		});

		final Button button3 = new Button(shell, SWT.PUSH);
		button3.setLayoutData(new GridData(SWT.BEGINNING, SWT.CENTER, false,
				false));
		button3.setText("Break all hells loose");
		button3.addSelectionListener(new SelectionAdapter() {
			public void widgetSelected(SelectionEvent e) {
				FEEDBACK.majorUserInitiatedActionIssue(null,
						"Hells broke loose so could not complete your command",
						null);
			}
		});

		shell.pack();
		shell.open();
		while (!shell.isDisposed()) {
			try {
				if (!display.readAndDispatch())
					display.sleep();
			} catch (Throwable e) {
				double random = Math.random();
				String foo = (random > 0.66 ? "A very very very very very long data"
						: (random > 0.33 ? "2" : "1"));
				FEEDBACK.silentRecovery(e, "Event loop exception", new Detail(
						"foo", foo),
						new Detail("another_detail", e.hashCode() % 5), new Detail(
								"some_additional_data", "42"),
								new Detail(
										"more_additional_data", "42"),
										new Detail(
												"even_more_additional_data", "42"));
			}
		}
		display.dispose();
	}

}
