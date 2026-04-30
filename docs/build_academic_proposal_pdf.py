from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ListStyle, ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


TITLE = "Learning-Augmented Robust Traffic Engineering for Resilient Software-Defined Networks"
SUBTITLE = "Final Project Proposal"
COURSE = "ECE GY 7363: Communications Networks II - Design and Algorithms"
DATE = "April 2026"

SECTIONS = [
    (
        "Abstract",
        [
            "This project proposes a learning-augmented framework for traffic engineering in software-defined networks under time-varying demand and link-failure uncertainty. The main idea is to combine short-horizon traffic prediction with optimization-based multi-commodity flow routing so that the controller can proactively reduce congestion while preserving performance under failures. The machine learning component predicts the next traffic matrix from historical observations, while the optimization component computes routing decisions that minimize maximum link utilization subject to flow conservation and capacity constraints. The resulting framework will be evaluated against shortest-path routing, optimization without prediction, and conservative robust baselines on standard network topologies and synthetic dynamic traffic traces. The expected outcome is a systematic study of when prediction-enhanced traffic engineering improves efficiency and resilience, and when robust non-predictive methods remain preferable.",
        ],
    ),
    (
        "1. Introduction and Motivation",
        [
            "Communication networks increasingly operate in environments where traffic demand changes rapidly over time and failures can occur with little warning. Traditional shortest-path routing is simple and computationally cheap, but it often reacts poorly to congestion because it does not explicitly reason about capacity sharing across commodities.",
            "Optimization-based traffic engineering improves this situation by accounting for the full demand matrix and link capacities, yet a purely reactive optimization approach may still perform suboptimally when demand shifts between control intervals. At the same time, machine learning has become a practical tool for traffic forecasting, anomaly detection, and resource management, but ML alone does not guarantee feasible routing decisions or provable capacity compliance.",
            "This project is motivated by the observation that prediction and optimization are complementary. If an accurate predictor can estimate the near-future traffic matrix, then a routing optimizer may use that information to allocate capacity more effectively before congestion materializes.",
        ],
    ),
    (
        "2. Problem Statement",
        [
            "The network is represented by a directed graph G = (V, E), where V is the set of nodes and E is the set of directed links. Each link (i, j) has capacity c_ij, and each source-destination pair is treated as a commodity with time-varying demand d_k(t).",
            "The design problem is to compute routing decisions that satisfy demand while controlling congestion and maintaining strong performance under failures. The central research question is whether short-term traffic prediction improves routing quality and resilience relative to shortest-path and non-predictive optimization baselines in dynamic software-defined networks.",
        ],
    ),
    (
        "3. Project Objectives",
        [
            "Formulate a dynamic traffic engineering model for a capacitated communication network.",
            "Train a machine learning model to predict near-future traffic matrices from historical data.",
            "Integrate predicted demand into a multi-commodity flow routing optimizer.",
            "Evaluate resilience under random and critical link-failure scenarios.",
            "Compare the proposed method against classical and optimization-based baselines.",
        ],
    ),
    (
        "4. Relevance to Course Themes",
        [
            "The proposal directly addresses network design problem modeling, optimization methods, multi-commodity flow routing, fair network design, resilient design, robust design, and machine-learning-based network management.",
            "It also satisfies the required final-project structure: problem definition, design model, solution methods, and performance evaluation.",
        ],
    ),
    (
        "5. Technical Approach",
        [
            "At each time step, the controller will observe recent traffic matrices, use a predictive model to estimate the next traffic matrix, solve a routing optimization problem using the predicted demand, and evaluate that routing under the realized traffic and possible link failures.",
            "The end-to-end pipeline is: historical traffic -> prediction model -> routing optimizer -> performance evaluation.",
        ],
    ),
    (
        "6. Machine Learning Component",
        [
            "The ML module will take a sliding window of recent traffic matrices as input and output a one-step-ahead traffic matrix prediction.",
            "The study will compare simple predictors such as moving average or linear regression against a recurrent model such as LSTM or GRU.",
            "The main model will likely be an LSTM because dynamic traffic exhibits temporal correlation and burst structure that sequence models can capture effectively.",
            "Prediction quality will be measured using MAE, RMSE, and relative traffic prediction error.",
        ],
    ),
    (
        "7. Optimization Component",
        [
            "The routing problem will be modeled as a multi-commodity flow program. For each commodity k and link (i, j), f_ij^k(t) denotes the amount of traffic routed on that link at time t.",
            "The model will enforce flow conservation, link-capacity constraints, and nonnegativity. To control congestion, an auxiliary utilization variable U(t) will be introduced and minimized so that the sum of flows on each link remains below U(t) times the link capacity.",
            "This yields a minimum-max-utilization routing policy, which is standard, interpretable, and well aligned with traffic engineering objectives.",
        ],
    ),
    (
        "8. Robustness and Resilience",
        [
            "The project will study resilience in two layers. First, scenario-based evaluation will test nominally optimized routing under random and critical link-failure scenarios.",
            "Second, if time permits, a simplified robust optimization extension will hedge against a predefined set of failures or demand perturbations directly in the solver.",
            "This structure ensures that the project always includes a meaningful resilience component even if the full robust model is computationally expensive.",
        ],
    ),
    (
        "9. Algorithms and Baselines",
        [
            "Baseline 1: shortest-path routing without optimization or prediction.",
            "Baseline 2: multi-commodity flow optimization using only the current observed traffic matrix.",
            "Baseline 3: conservative non-predictive routing with safety margins or worst-case demand estimates.",
            "Proposed method: learning-augmented routing that uses the predicted traffic matrix inside the optimization model.",
        ],
    ),
    (
        "10. Data, Topologies, and Experimental Setup",
        [
            "Experiments will use standard topologies such as NSFNET, Abilene, or GEANT. Additional synthetic topologies may be generated for stress testing.",
            "Traffic matrices will be created from periodic demand trends, random fluctuations, bursty spikes, and hotspot source-destination pairs so the resulting traces are realistic yet reproducible.",
            "Failure scenarios will include no-failure baseline cases, random single-link failures, critical-link failures, and traffic-spike cases combined with failures.",
        ],
    ),
    (
        "11. Evaluation Metrics",
        [
            "Maximum link utilization",
            "Average link utilization",
            "Fraction of demand satisfied",
            "Total routing cost",
            "Average path length",
            "Number of congested links",
            "Jain's fairness index",
            "Performance degradation under failure",
            "Prediction error of the ML model",
        ],
    ),
    (
        "12. Expected Contributions",
        [
            "A complete learning-plus-optimization traffic engineering framework.",
            "A rigorous comparison of predictive and non-predictive routing methods.",
            "A resilience analysis under traffic uncertainty and link failures.",
            "Actionable insight into the settings where ML-guided routing improves performance.",
        ],
    ),
    (
        "13. Implementation Plan",
        [
            "Programming language: Python",
            "Graph handling: networkx",
            "Optimization: cvxpy or pulp, with Gurobi or CPLEX if available",
            "Machine learning: PyTorch",
            "Data processing and plotting: numpy, pandas, matplotlib, seaborn",
        ],
    ),
    (
        "14. Work Plan and Timeline",
        [
            "Week 1: finalize problem statement, topology selection, and codebase organization.",
            "Week 2: build synthetic traffic generation and shortest-path baseline.",
            "Week 3: implement and validate the multi-commodity flow optimizer.",
            "Week 4: train baseline and LSTM traffic predictors.",
            "Week 5: integrate traffic prediction with routing optimization.",
            "Week 6: run resilience experiments and sensitivity studies.",
            "Week 7: analyze results and prepare the report, slides, and code package.",
        ],
    ),
    (
        "15. Risks and Mitigation",
        [
            "Optimization may become slow on larger topologies, so the project will begin with medium-size networks and expand only after the pipeline is validated.",
            "Traffic prediction may not help if the traces are too random, so prediction quality will be evaluated separately from routing performance.",
            "A full robust optimization model may be too expensive to complete, so scenario-based resilience evaluation is the first priority and the robust formulation is treated as an extension.",
        ],
    ),
    (
        "16. Why This Project is Well Positioned for a High Score",
        [
            "The proposal is highly relevant to the course and combines modern ML ideas with mathematically grounded optimization.",
            "It is deep enough to demonstrate substantial workload but structured enough to remain feasible within the project timeline.",
            "It should produce clear tables, utilization plots, failure-case comparisons, and fairness analyses, which will help the final presentation and report.",
        ],
    ),
    (
        "17. Conclusion",
        [
            "This proposal presents an end-to-end study of learning-augmented traffic engineering for resilient software-defined networks. By combining short-term traffic prediction with optimization-based multi-commodity flow routing, the project will investigate whether forecast-informed decisions can reduce congestion and improve robustness under failures.",
            "The framework is mathematically grounded, experimentally testable, and directly aligned with the goals of the course, making it a strong candidate for a high-quality final design project.",
        ],
    ),
]


def make_styles():
    styles = getSampleStyleSheet()
    styles.add(
        ParagraphStyle(
            name="PaperTitle",
            parent=styles["Title"],
            fontName="Helvetica-Bold",
            fontSize=18,
            leading=22,
            alignment=1,
            textColor=colors.HexColor("#17365D"),
            spaceAfter=8,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PaperMeta",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=10,
            leading=13,
            alignment=1,
            textColor=colors.HexColor("#555555"),
            spaceAfter=3,
        )
    )
    styles.add(
        ParagraphStyle(
            name="SectionHead",
            parent=styles["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            leading=15,
            textColor=colors.HexColor("#17365D"),
            spaceBefore=10,
            spaceAfter=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="PaperBody",
            parent=styles["BodyText"],
            fontName="Times-Roman",
            fontSize=10.5,
            leading=14,
            spaceAfter=5,
            alignment=4,
        )
    )
    styles.add(
        ParagraphStyle(
            name="CaptionSmall",
            parent=styles["BodyText"],
            fontName="Helvetica",
            fontSize=9,
            leading=11,
            textColor=colors.HexColor("#444444"),
            spaceAfter=6,
        )
    )
    styles.add(
        ListStyle(
            name="BulletList",
            leftIndent=18,
            rightIndent=0,
            bulletFontName="Helvetica",
            bulletFontSize=10,
            bulletIndent=6,
        )
    )
    return styles


def is_short_list(items):
    return len(items) >= 3 and all(len(item) < 120 for item in items)


def build_story(styles):
    story = [
        Spacer(1, 0.2 * inch),
        Paragraph(TITLE, styles["PaperTitle"]),
        Paragraph(SUBTITLE, styles["PaperMeta"]),
        Paragraph(COURSE, styles["PaperMeta"]),
        Paragraph(DATE, styles["PaperMeta"]),
        Spacer(1, 0.15 * inch),
    ]

    summary_table = Table(
        [
            ["Project Focus", "Learning-augmented traffic engineering under dynamic demand and failures"],
            ["Core Methods", "Traffic prediction, multi-commodity flow optimization, resilience evaluation"],
            ["Target Outcome", "Lower congestion and stronger performance relative to classical baselines"],
        ],
        colWidths=[1.55 * inch, 4.95 * inch],
        hAlign="LEFT",
    )
    summary_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#D9EAF7")),
                ("TEXTCOLOR", (0, 0), (-1, -1), colors.black),
                ("GRID", (0, 0), (-1, -1), 0.45, colors.HexColor("#9BBAD0")),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.8),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.extend([summary_table, Spacer(1, 0.15 * inch)])

    for heading, paragraphs in SECTIONS:
        story.append(Paragraph(heading, styles["SectionHead"]))
        if is_short_list(paragraphs):
            items = [ListItem(Paragraph(item, styles["PaperBody"])) for item in paragraphs]
            story.append(ListFlowable(items, bulletType="bullet", style=styles["BulletList"]))
            story.append(Spacer(1, 0.04 * inch))
        else:
            for para in paragraphs:
                story.append(Paragraph(para, styles["PaperBody"]))

    story.append(Spacer(1, 0.08 * inch))
    story.append(Paragraph("Planned Software Stack", styles["SectionHead"]))
    stack_table = Table(
        [
            ["Component", "Planned Tooling"],
            ["Graph and topology processing", "networkx"],
            ["Numerical processing", "numpy, pandas"],
            ["Optimization", "cvxpy or pulp; optional Gurobi/CPLEX"],
            ["Machine learning", "PyTorch"],
            ["Visualization", "matplotlib, seaborn"],
        ],
        colWidths=[2.35 * inch, 4.15 * inch],
        hAlign="LEFT",
    )
    stack_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#17365D")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTNAME", (0, 1), (-1, -1), "Times-Roman"),
                ("FONTSIZE", (0, 0), (-1, -1), 9.7),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#AAB7C4")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.whitesmoke, colors.HexColor("#F6FAFD")]),
            ]
        )
    )
    story.extend(
        [
            stack_table,
            Spacer(1, 0.06 * inch),
            Paragraph("Table 1. Planned implementation stack for the proposed project.", styles["CaptionSmall"]),
        ]
    )
    return story


def add_page_number(canvas, doc):
    canvas.saveState()
    canvas.setFont("Helvetica", 9)
    canvas.setFillColor(colors.HexColor("#444444"))
    canvas.drawRightString(7.25 * inch, 0.55 * inch, f"Page {doc.page}")
    canvas.restoreState()


def main():
    out_path = Path(__file__).resolve().parent / "ML_Network_Project_Proposal_Academic.pdf"
    styles = make_styles()
    story = build_story(styles)
    doc = SimpleDocTemplate(
        str(out_path),
        pagesize=letter,
        leftMargin=0.85 * inch,
        rightMargin=0.85 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
        title=TITLE,
        author=COURSE,
    )
    doc.build(story, onFirstPage=add_page_number, onLaterPages=add_page_number)


if __name__ == "__main__":
    main()
