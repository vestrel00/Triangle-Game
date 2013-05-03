package com.vestrel00.triangle;

import com.badlogic.gdx.backends.lwjgl.LwjglApplication;
import com.badlogic.gdx.backends.lwjgl.LwjglApplicationConfiguration;

public class Main {
	public static void main(String[] args) {
		LwjglApplicationConfiguration cfg = new LwjglApplicationConfiguration();
		cfg.title = "Triangle";
		cfg.useGL20 = true;
		// must be sync'ed
		cfg.width = 320;
		cfg.height = 320;
		
		new LwjglApplication(new Triangle(), cfg);
	}
}
