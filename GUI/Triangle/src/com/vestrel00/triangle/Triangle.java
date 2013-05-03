package com.vestrel00.triangle;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.net.Socket;
import java.util.ArrayList;
import java.util.List;

import com.badlogic.gdx.ApplicationListener;
import com.badlogic.gdx.Gdx;
import com.badlogic.gdx.graphics.Color;
import com.badlogic.gdx.graphics.GL10;
import com.badlogic.gdx.graphics.OrthographicCamera;
import com.badlogic.gdx.graphics.g2d.BitmapFont;
import com.badlogic.gdx.graphics.g2d.SpriteBatch;
import com.badlogic.gdx.graphics.glutils.ShapeRenderer;
import com.badlogic.gdx.graphics.glutils.ShapeRenderer.ShapeType;
import com.badlogic.gdx.utils.Disposable;
import com.badlogic.gdx.utils.StringBuilder;

public class Triangle implements ApplicationListener {

	private OrthographicCamera camera;
	private ShapeRenderer shape;
	private SpriteBatch batch;
	private BitmapFont font;

	// For server connection
	private Thread listenerThread;
	private ServerListener listener;

	// Game component
	private final int DIST_MULTIPLIER = 80;
	private final int[][] points = { { 0, 0 }, { 0, 1 }, { 0, 2 }, { 0, 3 },
			{ 1, 0 }, { 1, 1 }, { 1, 2 }, { 1, 3 }, { 2, 0 }, { 2, 1 },
			{ 2, 2 }, { 2, 3 }, { 3, 0 }, { 3, 1 }, { 3, 2 }, { 3, 3 } };
	private Player player1, player2;

	@Override
	public void create() {
		player1 = new Player("Player 1", Color.RED);
		player2 = new Player("Player 2", Color.BLUE);

		shape = new ShapeRenderer();
		batch = new SpriteBatch();
		font = new BitmapFont();

		// Must be sync'ed with desktop screen dimensions
		// int wh = 4*DIST_MULTIPLIER; 4 because it is a 4 by 4 matrix
		int wh = 320;
		camera = new OrthographicCamera();
		camera.setToOrtho(true, wh, wh);
		camera.position.x = 1.5f * DIST_MULTIPLIER;
		camera.position.y = 1.5f * DIST_MULTIPLIER;
		camera.update();

		shape.setProjectionMatrix(camera.combined);
		batch.setProjectionMatrix(camera.combined);

		Gdx.graphics.setContinuousRendering(false);

		listener = new ServerListener();
		listenerThread = new Thread(listener);
		listenerThread.start();

	}

	@Override
	public void render() {
		Gdx.gl.glClearColor(1, 1, 1, 1);
		Gdx.gl.glClear(GL10.GL_COLOR_BUFFER_BIT);

		// Draw the points
		shape.begin(ShapeType.FilledCircle);
		shape.setColor(Color.BLACK);
		for (int i = 0; i < points.length; i++)
			shape.filledCircle(points[i][0] * DIST_MULTIPLIER, points[i][1]
					* DIST_MULTIPLIER, 3);
		shape.end();

		// Draw the lines
		shape.begin(ShapeType.Line);
		player1.drawLines(shape);
		player2.drawLines(shape);
		shape.end();

		// Draw the Player scores
		batch.begin();
		font.setScale(1.0f, -1.0f);
		font.setColor(player1.color);
		font.draw(batch, player1.getScore(), camera.viewportWidth * -0.1f,
				camera.viewportHeight * -0.1f);
		font.setColor(player2.color);
		font.draw(batch, player2.getScore(), camera.viewportWidth * 0.6f,
				camera.viewportHeight * -0.1f);
		batch.end();
	}

	@Override
	public void dispose() {
		shape.dispose();
		listener.dispose();
		try {
			listenerThread.join();
		} catch (InterruptedException e) {
			e.printStackTrace();
		}
	}

	@Override
	public void resize(int width, int height) {
	}

	@Override
	public void pause() {
	}

	@Override
	public void resume() {
	}

	private class Player {

		// to avoid creation of a new string
		private static final String COLON = ": ";
		private StringBuilder builder;

		public List<Line> lines;
		public String name;
		public Color color;
		public int score;

		public Player(String name, Color color) {
			this.name = name;
			this.color = color;

			score = 0;
			lines = new ArrayList<Line>();
			builder = new StringBuilder();
		}

		public void drawLines(ShapeRenderer shape) {
			// abstract iterators may allocate new space in the heap
			// e.g. for (Line line:lines)
			shape.setColor(color);
			for (int i = 0; i < lines.size(); i++)
				lines.get(i).draw(shape);
		}

		public StringBuilder getScore() {
			builder.delete(0, builder.length);
			// return name + ": " + score creates garbage in the heap - avoid it
			builder.append(name);
			builder.append(COLON);
			builder.append(score);
			return builder;
		}

		public void update(String score, String line) {
			this.score = Integer.valueOf(score);
			this.lines.add(new Line(line));
			Gdx.graphics.requestRendering();
		}

	}

	private class Line {
		private int x1, y1, x2, y2;

		public Line(String line) {
			x1 = Integer.valueOf(String.valueOf(line.charAt(0)))
					* DIST_MULTIPLIER;
			y1 = Integer.valueOf(String.valueOf(line.charAt(1)))
					* DIST_MULTIPLIER;
			x2 = Integer.valueOf(String.valueOf(line.charAt(2)))
					* DIST_MULTIPLIER;
			y2 = Integer.valueOf(String.valueOf(line.charAt(3)))
					* DIST_MULTIPLIER;
		}

		public void draw(ShapeRenderer shape) {
			System.out.println(x1 + ", " + y1 + ", " + x2 + ", " + y2);
			shape.line(x1, y1, x2, y2);
		}
	}

	private class ServerListener implements Runnable, Disposable {

		private Socket socket;
		private BufferedReader in;
		private boolean isRunning = true;

		public ServerListener() {
			try {
				socket = new Socket("localhost", 8000);
				in = new BufferedReader(new InputStreamReader(
						socket.getInputStream()));
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

		@Override
		public void run() {
			while (isRunning) {
				try {
					// see TriangleGUIManager.sendAddLineResult in triangle.py
					// for the data format : playerId, playerScore, lineDrawn
					String data;
					String[] list = new String[3];
					if ((data = in.readLine()) == null)
						break;
					list = data.split(",");
					if (list[0].contentEquals("1"))
						player1.update(list[1], list[2]);
					else
						player2.update(list[1], list[2]);
				} catch (IOException e) {
					e.printStackTrace();
				}
			}
		}

		@Override
		public void dispose() {
			isRunning = false;
			try {
				socket.close();
			} catch (IOException e) {
				e.printStackTrace();
			}
		}

	}

}
